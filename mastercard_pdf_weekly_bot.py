#!/usr/bin/env python3
"""
Mastercard PDF Weekly Collector
Coleta PDFs semanalmente do Technical Resource Center > Announcements
Filtra por Publication Date da semana anterior
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
        logging.FileHandler('mastercard_weekly.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MastercardWeeklyBot:
    def __init__(self):
        self.download_dir = Path("downloads_weekly")
        self.pdf_dir = Path("pdfs_weekly")
        self.setup_directories()
        self.driver = None
        
    def setup_directories(self):
        """Cria diretórios necessários"""
        self.download_dir.mkdir(exist_ok=True)
        self.pdf_dir.mkdir(exist_ok=True)
        
        # Limpa diretórios anteriores
        for file in self.download_dir.glob("*"):
            file.unlink()
        for file in self.pdf_dir.glob("*"):
            if file.is_file():
                file.unlink()
                
        logger.info(f"Diretórios preparados: {self.download_dir}, {self.pdf_dir}")
        
    def get_previous_week_dates(self):
        """Calcula as datas da semana anterior"""
        today = datetime.now()
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        logger.info(f"🗓️ Semana anterior: {last_monday.strftime('%d %b %Y')} até {last_sunday.strftime('%d %b %Y')}")
        return last_monday, last_sunday
        
    def setup_chrome(self):
        """Configura Chrome"""
        chrome_options = Options()
        
        # Configurações de download
        download_path = str(self.download_dir.absolute())
        prefs = {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Configurações anti-detecção
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def login_and_navigate(self):
        """Faz login e navega para a seção correta"""
        logger.info("🚀 Iniciando navegação...")
        
        # Abre site
        self.driver.get("https://mastercardconnect.com")
        logger.info("Site carregado")
        
        # Aguarda login manual
        print("\n" + "="*60)
        print("🔑 FAÇA LOGIN MANUALMENTE")
        print("📧 Email: gabriela.braga@cloudwalk.io")
        print("🔒 Senha: Medemotivos!")
        print("="*60)
        input("Pressione ENTER quando estiver logado...")
        
        # Tenta navegar para Technical Resource Center
        logger.info("🔍 Procurando Technical Resource Center...")
        
        # Possíveis URLs diretas
        possible_urls = [
            "https://mastercardconnect.com/technical-resource-center",
            "https://mastercardconnect.com/resources/technical",
            "https://mastercardconnect.com/trc",
            "https://mastercardconnect.com/resources"
        ]
        
        trc_found = False
        for url in possible_urls:
            try:
                logger.info(f"Tentando URL: {url}")
                self.driver.get(url)
                time.sleep(3)
                
                if "404" not in self.driver.page_source.lower() and "not found" not in self.driver.page_source.lower():
                    logger.info(f"✅ Acessou TRC via: {url}")
                    trc_found = True
                    break
            except:
                continue
                
        if not trc_found:
            # Procura por links na página atual
            logger.info("Procurando links para TRC na página atual...")
            try:
                trc_links = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'Technical') or contains(text(), 'Resource') or contains(text(), 'Center')]")
                
                if trc_links:
                    logger.info(f"Encontrados {len(trc_links)} possíveis links para TRC")
                    for i, link in enumerate(trc_links[:3]):  # Tenta os primeiros 3
                        try:
                            logger.info(f"Tentando clicar no link: {link.text}")
                            self.driver.execute_script("arguments[0].click();", link)
                            time.sleep(3)
                            trc_found = True
                            break
                        except:
                            continue
            except:
                pass
                
        if not trc_found:
            logger.error("❌ Não conseguiu acessar Technical Resource Center")
            print("\n🔧 NAVEGAÇÃO MANUAL NECESSÁRIA")
            print("Por favor, navegue manualmente para Technical Resource Center > Announcements")
            input("Pressione ENTER quando estiver na página de Announcements...")
        else:
            # Procura Announcements
            self.navigate_to_announcements()
            
    def navigate_to_announcements(self):
        """Navega para a seção Announcements"""
        logger.info("🔍 Procurando Announcements...")
        
        # Aguarda página carregar
        time.sleep(3)
        
        try:
            # Procura por links de Announcements
            announcement_selectors = [
                "//a[contains(text(), 'Announcement')]",
                "//a[contains(text(), 'announcement')]",
                "//span[contains(text(), 'Announcement')]",
                "//div[contains(text(), 'Announcement')]"
            ]
            
            announcement_found = False
            for selector in announcement_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        logger.info(f"Tentando clicar em: {element.text}")
                        self.driver.execute_script("arguments[0].click();", element)
                        time.sleep(3)
                        announcement_found = True
                        break
                    if announcement_found:
                        break
                except:
                    continue
                    
            if not announcement_found:
                logger.warning("⚠️ Não encontrou link de Announcements automaticamente")
                print("\n🔧 Por favor, clique manualmente em 'Announcements'")
                input("Pressione ENTER quando estiver na página de Announcements...")
                
        except Exception as e:
            logger.error(f"Erro ao procurar Announcements: {e}")
            print("\n🔧 Navegue manualmente para Announcements")
            input("Pressione ENTER quando estiver na página de Announcements...")
            
    def find_and_download_weekly_pdfs(self):
        """Encontra e baixa PDFs da semana anterior"""
        logger.info("🔍 Procurando PDFs da semana anterior...")
        
        week_start, week_end = self.get_previous_week_dates()
        
        # Aguarda página carregar
        time.sleep(5)
        
        try:
            # Procura por todos os elementos de texto na página
            all_text_elements = self.driver.find_elements(By.XPATH, "//*[text()]")
            
            documents_found = []
            
            # Padrões de data para procurar
            date_patterns = [
                r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b',
                r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})\b',
                r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b',
                r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b'
            ]
            
            month_map = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            
            logger.info(f"Analisando {len(all_text_elements)} elementos...")
            
            for element in all_text_elements:
                try:
                    text = element.text.strip()
                    if not text or len(text) > 500:  # Ignora textos muito longos
                        continue
                        
                    # Procura datas no texto
                    for pattern in date_patterns:
                        matches = re.finditer(pattern, text, re.IGNORECASE)
                        
                        for match in matches:
                            try:
                                groups = match.groups()
                                
                                # Converte para datetime baseado no padrão
                                if len(groups) == 3:
                                    if groups[1] in month_map:  # DD Mon YYYY
                                        day, month_str, year = groups
                                        month = month_map[groups[1]]
                                    elif groups[0] in month_map:  # Mon DD YYYY
                                        month_str, day, year = groups
                                        month = month_map[groups[0]]
                                    else:  # DD/MM/YYYY ou YYYY-MM-DD
                                        if len(groups[0]) == 4:  # YYYY-MM-DD
                                            year, month, day = groups
                                        else:  # DD/MM/YYYY
                                            day, month, year = groups
                                        month = int(month)
                                    
                                    day = int(day)
                                    year = int(year)
                                    
                                    doc_date = datetime(year, month, day)
                                    
                                    # Verifica se está na semana anterior
                                    if week_start <= doc_date <= week_end:
                                        logger.info(f"📅 Documento da semana anterior: {doc_date.strftime('%d %b %Y')}")
                                        
                                        # Procura botão de download próximo
                                        download_link = self.find_download_near_element(element)
                                        if download_link:
                                            documents_found.append({
                                                'date': doc_date,
                                                'date_str': doc_date.strftime('%d %b %Y'),
                                                'element': element,
                                                'download_link': download_link,
                                                'text': text[:100]
                                            })
                                            
                            except ValueError:
                                continue
                                
                except Exception as e:
                    continue
                    
            # Remove duplicatas
            unique_docs = {}
            for doc in documents_found:
                key = doc['date_str']
                if key not in unique_docs:
                    unique_docs[key] = doc
                    
            documents_found = list(unique_docs.values())
            
            logger.info(f"�� Encontrados {len(documents_found)} documentos únicos da semana anterior")
            
            if not documents_found:
                logger.warning("⚠️ Nenhum documento da semana anterior encontrado")
                print("\n🔧 BUSCA MANUAL")
                print("Por favor, procure manualmente por documentos com Publication Date da semana anterior")
                print(f"Procure por datas entre {week_start.strftime('%d %b %Y')} e {week_end.strftime('%d %b %Y')}")
                
                # Mostra todos os elementos com datas encontrados
                print("\n📅 Todas as datas encontradas na página:")
                all_dates = []
                for element in all_text_elements:
                    text = element.text.strip()
                    if any(year in text for year in ['2024', '2025']):
                        if len(text) < 200:
                            all_dates.append(text)
                            
                for i, date_text in enumerate(all_dates[:20]):  # Primeiras 20
                    print(f"  {i+1}. {date_text}")
                    
                input("Pressione ENTER para continuar ou CTRL+C para sair...")
                return []
                
            # Faz download dos documentos encontrados
            return self.download_documents(documents_found)
            
        except Exception as e:
            logger.error(f"Erro ao procurar documentos: {e}")
            return []
            
    def find_download_near_element(self, element):
        """Encontra botão/link de download próximo ao elemento"""
        try:
            # Procura no mesmo elemento e parents
            current = element
            for _ in range(5):  # Sobe até 5 níveis na hierarquia
                try:
                    # Procura por botões/links de download
                    download_selectors = [
                        './/a[contains(@href, "download") or contains(@href, ".zip")]',
                        './/button[contains(@class, "download") or contains(text(), "Download")]',
                        './/a[contains(@class, "download") or contains(text(), "Download")]',
                        './/i[contains(@class, "download")]/..',
                        './/span[contains(text(), "Download")]/..'
                    ]
                    
                    for selector in download_selectors:
                        try:
                            download_elem = current.find_element(By.XPATH, selector)
                            return download_elem
                        except:
                            continue
                            
                    # Sobe um nível
                    current = current.find_element(By.XPATH, "./..")
                    
                except:
                    break
                    
            return None
            
        except Exception as e:
            return None
            
    def download_documents(self, documents):
        """Faz download dos documentos"""
        logger.info(f"📥 Iniciando download de {len(documents)} documentos...")
        
        downloaded_files = []
        
        for i, doc in enumerate(documents):
            try:
                logger.info(f"Baixando {i+1}/{len(documents)}: {doc['date_str']}")
                
                # Clica no botão de download
                self.driver.execute_script("arguments[0].scrollIntoView();", doc['download_link'])
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", doc['download_link'])
                
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
                    logger.warning(f"⚠️ Download falhou para {doc['date_str']}")
                    
                time.sleep(2)  # Pausa entre downloads
                
            except Exception as e:
                logger.error(f"Erro no download de {doc['date_str']}: {e}")
                continue
                
        logger.info(f"📥 Downloads concluídos: {len(downloaded_files)} arquivos")
        return downloaded_files
        
    def wait_for_download(self, timeout=60):
        """Aguarda download ser concluído"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            files = list(self.download_dir.glob("*"))
            complete_files = [f for f in files if not f.name.endswith('.crdownload')]
            
            if complete_files:
                # Retorna o arquivo mais recente
                newest_file = max(complete_files, key=lambda f: f.stat().st_mtime)
                return newest_file
                
            time.sleep(1)
            
        return None
        
    def extract_pdfs(self, downloaded_files):
        """Extrai PDFs dos arquivos baixados"""
        logger.info("📂 Extraindo PDFs...")
        
        extracted_pdfs = []
        
        for file_info in downloaded_files:
            file_path = file_info['file']
            
            try:
                if file_path.suffix.lower() == '.zip':
                    logger.info(f"Extraindo ZIP: {file_path.name}")
                    
                    extract_dir = self.pdf_dir / f"extracted_{file_info['date_str'].replace(' ', '_')}"
                    extract_dir.mkdir(exist_ok=True)
                    
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        for member in zip_ref.namelist():
                            if member.lower().endswith('.pdf'):
                                zip_ref.extract(member, extract_dir)
                                extracted_pdf = extract_dir / member
                                extracted_pdfs.append({
                                    'pdf_path': extracted_pdf,
                                    'date': file_info['date'],
                                    'date_str': file_info['date_str']
                                })
                                logger.info(f"✅ PDF extraído: {member}")
                                
                elif file_path.suffix.lower() == '.pdf':
                    # Já é PDF, apenas copia
                    pdf_dest = self.pdf_dir / file_path.name
                    shutil.copy2(file_path, pdf_dest)
                    extracted_pdfs.append({
                        'pdf_path': pdf_dest,
                        'date': file_info['date'],
                        'date_str': file_info['date_str']
                    })
                    logger.info(f"✅ PDF copiado: {file_path.name}")
                    
            except Exception as e:
                logger.error(f"Erro ao extrair {file_path}: {e}")
                continue
                
        logger.info(f"📂 Total de PDFs extraídos: {len(extracted_pdfs)}")
        return extracted_pdfs
        
    def run_weekly_collection(self):
        """Executa coleta semanal completa"""
        logger.info("🚀 INICIANDO COLETA SEMANAL DE PDFs MASTERCARD")
        print("=" * 60)
        
        try:
            # Mostra período
            week_start, week_end = self.get_previous_week_dates()
            
            # Configura Chrome
            self.setup_chrome()
            
            # Login e navegação
            self.login_and_navigate()
            
            # Busca e download
            downloaded_files = self.find_and_download_weekly_pdfs()
            
            if not downloaded_files:
                logger.warning("⚠️ Nenhum arquivo foi baixado")
                return False
                
            # Extrai PDFs
            extracted_pdfs = self.extract_pdfs(downloaded_files)
            
            # Relatório final
            logger.info("✅ COLETA CONCLUÍDA")
            logger.info(f"📅 Período: {week_start.strftime('%d %b %Y')} - {week_end.strftime('%d %b %Y')}")
            logger.info(f"📥 Arquivos baixados: {len(downloaded_files)}")
            logger.info(f"📄 PDFs extraídos: {len(extracted_pdfs)}")
            
            print("\n📋 ARQUIVOS COLETADOS:")
            for pdf in extracted_pdfs:
                print(f"  • {pdf['pdf_path'].name} ({pdf['date_str']})")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante coleta: {e}")
            return False
            
        finally:
            if self.driver:
                logger.info("Fechando navegador...")
                time.sleep(2)
                self.driver.quit()

def main():
    bot = MastercardWeeklyBot()
    
    try:
        success = bot.run_weekly_collection()
        
        if success:
            print("\n�� COLETA EXECUTADA COM SUCESSO!")
        else:
            print("\n❌ COLETA FALHOU")
            
    except KeyboardInterrupt:
        print("\n⏹️ Coleta interrompida pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")

if __name__ == "__main__":
    main()
