#!/usr/bin/env python3
"""
Mastercard PDF Weekly Collector - VERSÃO CORRIGIDA
Procura especificamente por "Publication Date:" e filtra pela semana anterior
"""

import os
import time
import zipfile
import shutil
import re
from datetime import datetime, timedelta
from pathlib import Path
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mastercard_weekly_fixed.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MastercardWeeklyCollector:
    def __init__(self):
        self.download_dir = Path("downloads_weekly")
        self.pdf_dir = Path("pdfs_weekly")
        self.setup_directories()
        self.driver = None
        
    def setup_directories(self):
        """Cria e limpa diretórios"""
        self.download_dir.mkdir(exist_ok=True)
        self.pdf_dir.mkdir(exist_ok=True)
        
        # Limpa arquivos anteriores
        for file in self.download_dir.glob("*"):
            if file.is_file():
                file.unlink()
        for file in self.pdf_dir.glob("*"):
            if file.is_file():
                file.unlink()
                
        logger.info(f"Diretórios preparados: {self.download_dir}, {self.pdf_dir}")
        
    def get_previous_week_dates(self):
        """Calcula datas da semana anterior"""
        today = datetime.now()
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        logger.info(f"📅 Hoje: {today.strftime('%d %b %Y')}")
        logger.info(f"📅 Semana anterior: {last_monday.strftime('%d %b %Y')} até {last_sunday.strftime('%d %b %Y')}")
        return last_monday, last_sunday
        
    def setup_chrome(self):
        """Configura Chrome"""
        chrome_options = Options()
        
        # Download settings
        download_path = str(self.download_dir.absolute())
        prefs = {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Anti-detection
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def open_and_login(self):
        """Abre site e aguarda login manual"""
        logger.info("🌐 Abrindo mastercardconnect.com...")
        self.driver.get("https://mastercardconnect.com")
        time.sleep(3)
        
        print("\n" + "="*60)
        print("🔑 FAÇA LOGIN MANUALMENTE")
        print("📧 Email: gabriela.braga@cloudwalk.io") 
        print("🔒 Senha: Medemotivos!")
        print("📍 Depois navegue para: Technical Resource Center > Announcements")
        print("="*60)
        
        input("Pressione ENTER quando estiver na página de Announcements...")
        
    def find_publication_date_documents(self):
        """Encontra documentos com Publication Date da semana anterior"""
        logger.info("🔍 Procurando documentos com Publication Date da semana anterior...")
        
        week_start, week_end = self.get_previous_week_dates()
        
        # Aguarda página carregar completamente
        time.sleep(5)
        
        try:
            # Procura especificamente por elementos que contêm "Publication Date:"
            pub_date_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Publication Date:')]")
            
            logger.info(f"📋 Encontrados {len(pub_date_elements)} elementos com 'Publication Date:'")
            
            documents_to_download = []
            
            for element in pub_date_elements:
                try:
                    text = element.text.strip()
                    logger.info(f"📄 Analisando: {text}")
                    
                    # Extrai a data após "Publication Date:"
                    match = re.search(r'Publication Date:\s*(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})', text, re.IGNORECASE)
                    
                    if match:
                        day, month_str, year = match.groups()
                        
                        # Converte mês para número
                        month_map = {
                            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                        }
                        
                        try:
                            pub_date = datetime(int(year), month_map[month_str], int(day))
                            logger.info(f"📅 Data encontrada: {pub_date.strftime('%d %b %Y')}")
                            
                            # Verifica se está na semana anterior
                            if week_start <= pub_date <= week_end:
                                logger.info(f"✅ Documento da semana anterior encontrado: {pub_date.strftime('%d %b %Y')}")
                                
                                # Procura pelo botão de download próximo
                                download_button = self.find_download_button(element)
                                
                                if download_button:
                                    documents_to_download.append({
                                        'date': pub_date,
                                        'date_str': pub_date.strftime('%d %b %Y'),
                                        'element': element,
                                        'download_button': download_button,
                                        'text': text[:100]
                                    })
                                    logger.info(f"📥 Botão de download encontrado para {pub_date.strftime('%d %b %Y')}")
                                else:
                                    logger.warning(f"⚠️ Botão de download não encontrado para {pub_date.strftime('%d %b %Y')}")
                            else:
                                logger.info(f"❌ Data fora do período: {pub_date.strftime('%d %b %Y')}")
                                
                        except (ValueError, KeyError) as e:
                            logger.error(f"Erro ao processar data: {e}")
                            
                    else:
                        logger.warning(f"⚠️ Padrão de data não encontrado em: {text[:50]}...")
                        
                except Exception as e:
                    logger.error(f"Erro ao processar elemento: {e}")
                    continue
                    
            logger.info(f"📋 Total de documentos da semana anterior: {len(documents_to_download)}")
            
            if not documents_to_download:
                logger.warning("⚠️ Nenhum documento da semana anterior encontrado!")
                
                # Mostra todos os Publication Dates encontrados para debug  
                logger.info("🔧 DEBUG - Todas as Publication Dates encontradas:")
                for elem in pub_date_elements[:10]:  # Primeiros 10
                    logger.info(f"  - {elem.text.strip()[:100]}...")
                    
            return documents_to_download
            
        except Exception as e:
            logger.error(f"Erro ao procurar documentos: {e}")
            return []
            
    def find_download_button(self, pub_date_element):
        """Encontra botão de download próximo ao elemento de Publication Date"""
        try:
            # Estratégia 1: Procura no mesmo container/card
            # Sobe na hierarquia para encontrar o container do documento
            current = pub_date_element
            
            for level in range(10):  # Sobe até 10 níveis
                try:
                    # Procura por botão/link de download no nível atual
                    download_selectors = [
                        './/a[contains(@href, "download")]',
                        './/a[contains(@href, ".zip")]', 
                        './/button[contains(@class, "download")]',
                        './/a[contains(@class, "download")]',
                        './/i[contains(@class, "download")]/..',
                        './/span[contains(@class, "download")]/..',
                        './/*[contains(@title, "Download")]',
                        './/*[contains(@alt, "Download")]'
                    ]
                    
                    for selector in download_selectors:
                        try:
                            download_elem = current.find_element(By.XPATH, selector)
                            logger.info(f"🎯 Botão de download encontrado no nível {level} com seletor: {selector}")
                            return download_elem
                        except:
                            continue
                            
                    # Sobe um nível na hierarquia
                    current = current.find_element(By.XPATH, "./..")
                    
                except:
                    break
                    
            # Estratégia 2: Procura por ícone de seta para baixo (como na imagem)
            try:
                # Procura por elementos que podem ser ícones de download
                parent_container = pub_date_element.find_element(By.XPATH, "./ancestor::*[position()<=5]")
                
                icon_selectors = [
                    './/i[contains(@class, "fa-download")]',
                    './/i[contains(@class, "download")]',
                    './/*[contains(@class, "icon-download")]',
                    './/*[contains(@class, "arrow-down")]',
                    './/*[text()="⬇"]',  # Unicode arrow
                    './/*[contains(@class, "material-icons") and text()="file_download"]'
                ]
                
                for selector in icon_selectors:
                    try:
                        icon_elem = parent_container.find_element(By.XPATH, selector)
                        # Se é um ícone, procura pelo elemento clicável pai
                        clickable_parent = icon_elem.find_element(By.XPATH, "./ancestor::a[1]")
                        logger.info(f"🎯 Ícone de download encontrado: {selector}")
                        return clickable_parent
                    except:
                        continue
                        
            except:
                pass
                
            logger.warning("⚠️ Botão de download não encontrado")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao procurar botão de download: {e}")
            return None
            
    def download_documents(self, documents):
        """Faz download dos documentos"""
        logger.info(f"📥 Iniciando downloads de {len(documents)} documentos...")
        
        downloaded_files = []
        
        for i, doc in enumerate(documents):
            try:
                logger.info(f"📥 Baixando {i+1}/{len(documents)}: {doc['date_str']}")
                
                # Scroll até o elemento ficar visível
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", doc['download_button'])
                time.sleep(1)
                
                # Clica no botão de download
                self.driver.execute_script("arguments[0].click();", doc['download_button'])
                logger.info(f"🖱️ Clicou no botão de download para {doc['date_str']}")
                
                # Aguarda download
                downloaded_file = self.wait_for_download()
                
                if downloaded_file:
                    downloaded_files.append({
                        'file': downloaded_file,
                        'date': doc['date'],
                        'date_str': doc['date_str']
                    })
                    logger.info(f"✅ Download concluído: {downloaded_file.name}")
                else:
                    logger.warning(f"⚠️ Download não detectado para {doc['date_str']}")
                    
                # Pausa entre downloads
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ Erro no download de {doc['date_str']}: {e}")
                continue
                
        logger.info(f"📥 Downloads concluídos: {len(downloaded_files)} de {len(documents)} arquivos")
        return downloaded_files
        
    def wait_for_download(self, timeout=60):
        """Aguarda arquivo ser baixado"""
        logger.info("⏳ Aguardando download...")
        start_time = time.time()
        initial_files = set(f.name for f in self.download_dir.glob("*"))
        
        while time.time() - start_time < timeout:
            current_files = set(f.name for f in self.download_dir.glob("*"))
            new_files = current_files - initial_files
            
            # Verifica se há arquivos novos e completos (não .crdownload)
            complete_new_files = [f for f in new_files if not f.endswith('.crdownload')]
            
            if complete_new_files:
                newest_file = self.download_dir / complete_new_files[0]
                logger.info(f"✅ Arquivo baixado: {newest_file.name}")
                return newest_file
                
            time.sleep(2)
            
        logger.warning("⚠️ Timeout no download")
        return None
        
    def extract_pdfs(self, downloaded_files):
        """Extrai PDFs dos ZIPs"""
        logger.info("📂 Extraindo PDFs dos arquivos baixados...")
        
        extracted_pdfs = []
        
        for file_info in downloaded_files:
            file_path = file_info['file']
            
            try:
                if file_path.suffix.lower() == '.zip':
                    logger.info(f"📦 Extraindo ZIP: {file_path.name}")
                    
                    extract_dir = self.pdf_dir / f"extracted_{file_info['date_str'].replace(' ', '_')}"
                    extract_dir.mkdir(exist_ok=True)
                    
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        pdf_count = 0
                        for member in zip_ref.namelist():
                            if member.lower().endswith('.pdf'):
                                zip_ref.extract(member, extract_dir)
                                extracted_pdf = extract_dir / member
                                extracted_pdfs.append({
                                    'pdf_path': extracted_pdf,
                                    'date': file_info['date'],
                                    'date_str': file_info['date_str'],
                                    'original_zip': file_path.name
                                })
                                pdf_count += 1
                                logger.info(f"📄 PDF extraído: {member}")
                                
                        logger.info(f"✅ {pdf_count} PDFs extraídos de {file_path.name}")
                        
                elif file_path.suffix.lower() == '.pdf':
                    # Já é PDF
                    pdf_dest = self.pdf_dir / file_path.name
                    shutil.copy2(file_path, pdf_dest)
                    extracted_pdfs.append({
                        'pdf_path': pdf_dest,
                        'date': file_info['date'],
                        'date_str': file_info['date_str'],
                        'original_zip': None
                    })
                    logger.info(f"📄 PDF copiado: {file_path.name}")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao extrair {file_path}: {e}")
                continue
                
        logger.info(f"📂 Total de PDFs extraídos: {len(extracted_pdfs)}")
        return extracted_pdfs
        
    def run_collection(self):
        """Executa coleta completa"""
        logger.info("🚀 INICIANDO COLETA SEMANAL DE PDFs MASTERCARD")
        print("=" * 80)
        
        try:
            # Mostra período alvo
            week_start, week_end = self.get_previous_week_dates()
            print(f"🎯 PERÍODO ALVO: {week_start.strftime('%d %b %Y')} até {week_end.strftime('%d %b %Y')}")
            
            # Setup
            self.setup_chrome()
            
            # Login e navegação
            self.open_and_login()
            
            # Procura documentos
            documents = self.find_publication_date_documents()
            
            if not documents:
                logger.error("❌ Nenhum documento encontrado para download")
                return False
                
            # Downloads
            downloaded_files = self.download_documents(documents)
            
            if not downloaded_files:
                logger.error("❌ Nenhum arquivo foi baixado")
                return False
                
            # Extração
            extracted_pdfs = self.extract_pdfs(downloaded_files)
            
            # Relatório final
            print("\n" + "=" * 80)
            print("✅ COLETA CONCLUÍDA COM SUCESSO!")
            print(f"📅 Período: {week_start.strftime('%d %b %Y')} - {week_end.strftime('%d %b %Y')}")
            print(f"📋 Documentos encontrados: {len(documents)}")
            print(f"📥 Arquivos baixados: {len(downloaded_files)}")
            print(f"📄 PDFs extraídos: {len(extracted_pdfs)}")
            
            if extracted_pdfs:
                print("\n📁 ARQUIVOS COLETADOS:")
                for pdf in extracted_pdfs:
                    zip_info = f" (de {pdf['original_zip']})" if pdf['original_zip'] else ""
                    print(f"  • {pdf['pdf_path'].name} - {pdf['date_str']}{zip_info}")
                    
            print("=" * 80)
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante coleta: {e}")
            return False
            
        finally:
            if self.driver:
                input("\nPressione ENTER para fechar o navegador...")
                self.driver.quit()
                logger.info("🔚 Navegador fechado")

def main():
    collector = MastercardWeeklyCollector()
    
    try:
        success = collector.run_collection()
        
        if success:
            print("\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
            print("📁 Verifique a pasta 'pdfs_weekly' para os arquivos coletados")
        else:
            print("\n❌ PROCESSO FALHOU")
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo interrompido pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")

if __name__ == "__main__":
    main()
