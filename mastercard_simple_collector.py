#!/usr/bin/env python3
"""
Mastercard Simple Collector
Abordagem simplificada - você navega, eu coleto
"""

import time
import zipfile
import shutil
import re
from datetime import datetime, timedelta
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class SimpleCollector:
    def __init__(self):
        self.download_dir = Path("downloads_simple")
        self.pdf_dir = Path("pdfs_simple")
        self.setup_directories()
        self.driver = None
        
    def setup_directories(self):
        """Prepara diretórios"""
        self.download_dir.mkdir(exist_ok=True)
        self.pdf_dir.mkdir(exist_ok=True)
        
        # Limpa arquivos anteriores
        for file in self.download_dir.glob("*"):
            if file.is_file():
                file.unlink()
        for file in self.pdf_dir.glob("*"):
            if file.is_file():
                file.unlink()
                
        print(f"✅ Diretórios preparados: {self.download_dir}, {self.pdf_dir}")
        
    def get_target_week(self):
        """Calcula semana anterior"""
        today = datetime.now()
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        print(f"🗓️ Hoje: {today.strftime('%d %b %Y')}")
        print(f"🎯 Semana alvo: {last_monday.strftime('%d %b %Y')} até {last_sunday.strftime('%d %b %Y')}")
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
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def open_site_and_wait(self):
        """Abre site e aguarda navegação manual"""
        print("\n🌐 Abrindo mastercardconnect.com...")
        self.driver.get("https://mastercardconnect.com")
        time.sleep(3)
        
        print("\n" + "="*70)
        print("🎯 NAVEGAÇÃO MANUAL NECESSÁRIA")
        print("1. Faça login no site")
        print("2. Navegue para: Technical Resource Center")
        print("3. Clique em: Announcements")
        print("4. Aguarde a página carregar completamente")
        print("="*70)
        
        input("Pressione ENTER quando estiver na página de Announcements...")
        
        # Aguarda mais um pouco para garantir carregamento
        print("⏳ Aguardando página carregar...")
        time.sleep(5)
        
    def find_all_dates_on_page(self):
        """Encontra TODAS as datas na página"""
        print(f"\n🔍 Analisando página: {self.driver.current_url}")
        
        # Procura por QUALQUER elemento que contenha anos
        year_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '2025') or contains(text(), '2024')]")
        
        print(f"📋 Encontrados {len(year_elements)} elementos com anos")
        
        # Padrões de data para extrair
        date_patterns = [
            r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})',
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})'
        ]
        
        month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        
        found_dates = []
        
        for element in year_elements:
            try:
                text = element.text.strip()
                if not text or len(text) > 300:  # Ignora textos muito longos
                    continue
                    
                # Procura datas no texto
                for pattern in date_patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    
                    for match in matches:
                        try:
                            groups = match.groups()
                            
                            # Converte para datetime
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
                                
                                found_dates.append({
                                    'date': doc_date,
                                    'date_str': doc_date.strftime('%d %b %Y'),
                                    'element': element,
                                    'full_text': text,
                                    'matched_text': match.group()
                                })
                                
                        except (ValueError, KeyError):
                            continue
                            
            except Exception as e:
                continue
                
        # Remove duplicatas por data
        unique_dates = {}
        for item in found_dates:
            key = item['date_str']
            if key not in unique_dates:
                unique_dates[key] = item
                
        found_dates = list(unique_dates.values())
        
        # Ordena por data
        found_dates.sort(key=lambda x: x['date'])
        
        print(f"📅 Datas únicas encontradas: {len(found_dates)}")
        
        return found_dates
        
    def filter_target_week(self, all_dates):
        """Filtra datas da semana alvo"""
        week_start, week_end = self.get_target_week()
        
        target_dates = []
        
        for item in all_dates:
            if week_start <= item['date'] <= week_end:
                target_dates.append(item)
                
        print(f"\n🎯 Documentos da semana alvo ({week_start.strftime('%d %b')} - {week_end.strftime('%d %b')}):")
        
        if target_dates:
            for i, item in enumerate(target_dates):
                print(f"  {i+1}. {item['date_str']} - {item['full_text'][:80]}...")
        else:
            print("  ❌ Nenhum documento da semana alvo encontrado")
            
            # Mostra datas próximas para referência
            print(f"\n📅 Todas as datas encontradas (para referência):")
            for i, item in enumerate(all_dates[:10]):  # Primeiras 10
                print(f"  {i+1}. {item['date_str']} - {item['full_text'][:80]}...")
                
        return target_dates
        
    def find_download_buttons(self, target_documents):
        """Encontra botões de download para os documentos"""
        documents_with_downloads = []
        
        print(f"\n🔍 Procurando botões de download para {len(target_documents)} documentos...")
        
        for doc in target_documents:
            print(f"\n📄 Procurando download para: {doc['date_str']}")
            
            # Estratégias para encontrar botão de download
            download_button = None
            
            # Estratégia 1: Procura no mesmo elemento e pais
            current = doc['element']
            for level in range(8):  # Sobe até 8 níveis
                try:
                    # Seletores de download
                    selectors = [
                        './/a[contains(@href, "download") or contains(@href, ".zip")]',
                        './/button[contains(@class, "download")]',
                        './/a[contains(@class, "download")]',
                        './/i[contains(@class, "download")]/..',
                        './/*[contains(@title, "Download")]',
                        './/*[contains(text(), "Download")]'
                    ]
                    
                    for selector in selectors:
                        try:
                            download_button = current.find_element(By.XPATH, selector)
                            print(f"  ✅ Botão encontrado no nível {level}: {selector}")
                            break
                        except:
                            continue
                            
                    if download_button:
                        break
                        
                    # Sobe um nível
                    current = current.find_element(By.XPATH, "./..")
                    
                except:
                    break
                    
            if download_button:
                documents_with_downloads.append({
                    'date': doc['date'],
                    'date_str': doc['date_str'],
                    'element': doc['element'],
                    'download_button': download_button,
                    'text': doc['full_text']
                })
                print(f"  ✅ Download disponível para {doc['date_str']}")
            else:
                print(f"  ❌ Download não encontrado para {doc['date_str']}")
                
        print(f"\n📥 Total de documentos com download: {len(documents_with_downloads)}")
        return documents_with_downloads
        
    def download_files(self, documents):
        """Faz download dos arquivos"""
        print(f"\n📥 Iniciando downloads de {len(documents)} documentos...")
        
        downloaded_files = []
        
        for i, doc in enumerate(documents):
            try:
                print(f"\n📥 Download {i+1}/{len(documents)}: {doc['date_str']}")
                
                # Scroll para o elemento
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", doc['download_button'])
                time.sleep(2)
                
                # Clica no download
                self.driver.execute_script("arguments[0].click();", doc['download_button'])
                print(f"  🖱️ Clicou no botão de download")
                
                # Aguarda download
                downloaded_file = self.wait_for_download()
                
                if downloaded_file:
                    downloaded_files.append({
                        'file': downloaded_file,
                        'date': doc['date'],
                        'date_str': doc['date_str']
                    })
                    print(f"  ✅ Arquivo baixado: {downloaded_file.name}")
                else:
                    print(f"  ❌ Download falhou")
                    
                time.sleep(3)  # Pausa entre downloads
                
            except Exception as e:
                print(f"  ❌ Erro no download: {e}")
                continue
                
        print(f"\n📥 Downloads concluídos: {len(downloaded_files)} de {len(documents)}")
        return downloaded_files
        
    def wait_for_download(self, timeout=60):
        """Aguarda download"""
        start_time = time.time()
        initial_files = set(f.name for f in self.download_dir.glob("*"))
        
        while time.time() - start_time < timeout:
            current_files = set(f.name for f in self.download_dir.glob("*"))
            new_files = current_files - initial_files
            
            complete_files = [f for f in new_files if not f.endswith('.crdownload')]
            
            if complete_files:
                return self.download_dir / complete_files[0]
                
            time.sleep(2)
            
        return None
        
    def extract_pdfs(self, downloaded_files):
        """Extrai PDFs"""
        print(f"\n📂 Extraindo PDFs de {len(downloaded_files)} arquivos...")
        
        extracted_pdfs = []
        
        for file_info in downloaded_files:
            file_path = file_info['file']
            
            try:
                if file_path.suffix.lower() == '.zip':
                    print(f"📦 Extraindo ZIP: {file_path.name}")
                    
                    extract_dir = self.pdf_dir / f"extracted_{file_info['date_str'].replace(' ', '_')}"
                    extract_dir.mkdir(exist_ok=True)
                    
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        for member in zip_ref.namelist():
                            if member.lower().endswith('.pdf'):
                                zip_ref.extract(member, extract_dir)
                                extracted_pdf = extract_dir / member
                                extracted_pdfs.append({
                                    'pdf_path': extracted_pdf,
                                    'date_str': file_info['date_str'],
                                    'original_zip': file_path.name
                                })
                                print(f"  📄 PDF extraído: {member}")
                                
                elif file_path.suffix.lower() == '.pdf':
                    pdf_dest = self.pdf_dir / file_path.name
                    shutil.copy2(file_path, pdf_dest)
                    extracted_pdfs.append({
                        'pdf_path': pdf_dest,
                        'date_str': file_info['date_str'],
                        'original_zip': None
                    })
                    print(f"📄 PDF copiado: {file_path.name}")
                    
            except Exception as e:
                print(f"❌ Erro ao extrair {file_path}: {e}")
                continue
                
        print(f"📂 PDFs extraídos: {len(extracted_pdfs)}")
        return extracted_pdfs
        
    def run_collection(self):
        """Executa coleta completa"""
        print("🚀 MASTERCARD SIMPLE COLLECTOR")
        print("=" * 60)
        
        try:
            # Setup
            week_start, week_end = self.get_target_week()
            self.setup_chrome()
            
            # Navegação manual
            self.open_site_and_wait()
            
            # Busca todas as datas
            all_dates = self.find_all_dates_on_page()
            
            if not all_dates:
                print("❌ Nenhuma data encontrada na página")
                print("💡 Certifique-se de estar na página de Announcements")
                return False
                
            # Filtra semana alvo
            target_dates = self.filter_target_week(all_dates)
            
            if not target_dates:
                print("❌ Nenhum documento da semana alvo")
                return False
                
            # Procura downloads
            documents_with_downloads = self.find_download_buttons(target_dates)
            
            if not documents_with_downloads:
                print("❌ Nenhum botão de download encontrado")
                return False
                
            # Downloads
            downloaded_files = self.download_files(documents_with_downloads)
            
            if not downloaded_files:
                print("❌ Nenhum arquivo baixado")
                return False
                
            # Extração
            extracted_pdfs = self.extract_pdfs(downloaded_files)
            
            # Relatório final
            print("\n" + "="*60)
            print("✅ COLETA CONCLUÍDA!")
            print(f"📅 Período: {week_start.strftime('%d %b')} - {week_end.strftime('%d %b %Y')}")
            print(f"📋 Documentos encontrados: {len(target_dates)}")
            print(f"📥 Arquivos baixados: {len(downloaded_files)}")
            print(f"📄 PDFs extraídos: {len(extracted_pdfs)}")
            
            if extracted_pdfs:
                print("\n📁 ARQUIVOS COLETADOS:")
                for pdf in extracted_pdfs:
                    zip_info = f" (de {pdf['original_zip']})" if pdf['original_zip'] else ""
                    print(f"  • {pdf['pdf_path'].name} - {pdf['date_str']}{zip_info}")
                    
            return True
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
            
        finally:
            if self.driver:
                input("\nPressione ENTER para fechar o navegador...")
                self.driver.quit()

def main():
    collector = SimpleCollector()
    
    try:
        success = collector.run_collection()
        
        if success:
            print("\n🎉 SUCESSO! Verifique a pasta 'pdfs_simple'")
        else:
            print("\n❌ FALHOU")
            
    except KeyboardInterrupt:
        print("\n⏹️ Interrompido pelo usuário")

if __name__ == "__main__":
    main()
