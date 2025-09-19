#!/usr/bin/env python3
"""
Mastercard Icon Downloader
Clica especificamente no ícone de download (seta para baixo) de cada documento
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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class IconDownloader:
    def __init__(self):
        self.download_dir = Path("downloads_icon")
        self.pdf_dir = Path("pdfs_icon")
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
        
    def get_target_date_range(self):
        """Calcula período: da quarta anterior até hoje"""
        today = datetime.now()
        
        # Encontra a quarta-feira anterior
        days_since_wednesday = (today.weekday() - 2) % 7
        if days_since_wednesday == 0 and today.weekday() == 2:
            last_wednesday = today - timedelta(days=7)
        else:
            last_wednesday = today - timedelta(days=days_since_wednesday)
            
        if last_wednesday > today:
            last_wednesday = last_wednesday - timedelta(days=7)
            
        print(f"🗓️ Hoje: {today.strftime('%d %b %Y (%A)')}")
        print(f"🎯 Período: {last_wednesday.strftime('%d %b %Y')} até {today.strftime('%d %b %Y')}")
        
        return last_wednesday, today
        
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
        
    def open_and_navigate(self):
        """Abre e navega para a página de announcements"""
        print("\n🌐 Abrindo mastercardconnect.com...")
        self.driver.get("https://mastercardconnect.com")
        time.sleep(3)
        
        range_start, range_end = self.get_target_date_range()
        
        print("\n" + "="*80)
        print("🎯 NAVEGAÇÃO MANUAL")
        print("")
        print("1. 🔑 Faça login")
        print("2. 🏢 Vá para Technical Resource Center")
        print("3. 📢 Clique em Announcements")
        print("4. 👀 Aguarde ver os documentos com ícones de download")
        print("")
        print(f"🎯 VAMOS BAIXAR DOCUMENTOS DE: {range_start.strftime('%d %b')} até {range_end.strftime('%d %b %Y')}")
        print("="*80)
        
        input("Pressione ENTER quando estiver vendo os documentos com ícones...")
        
        # Gerencia abas se necessário
        all_tabs = self.driver.window_handles
        if len(all_tabs) > 1:
            print(f"\n📋 {len(all_tabs)} abas detectadas")
            for i, tab in enumerate(all_tabs):
                self.driver.switch_to.window(tab)
                time.sleep(1)
                print(f"  {i+1}. {self.driver.title[:50]}...")
                
            choice = input(f"Qual aba usar? (1-{len(all_tabs)}): ")
            try:
                self.driver.switch_to.window(all_tabs[int(choice)-1])
                print("✅ Aba selecionada")
            except:
                print("❌ Usando aba atual")
                
    def find_documents_with_download_icons(self):
        """Encontra documentos no período que tenham ícones de download"""
        print(f"\n🔍 Procurando documentos com ícones de download...")
        
        range_start, range_end = self.get_target_date_range()
        
        # Aguarda carregamento
        time.sleep(8)
        
        # Estratégia: Encontrar todos os ícones de download primeiro
        print("📥 Procurando ícones de download na página...")
        
        # Seletores para ícones de download (seta para baixo)
        download_icon_selectors = [
            # Ícones Font Awesome
            'i[class*="fa-download"]',
            'i[class*="fa-arrow-down"]', 
            'i[class*="download"]',
            # Ícones Material
            'i[class*="material-icons"]:contains("file_download")',
            'i[class*="material-icons"]:contains("download")',
            'i[class*="material-icons"]:contains("arrow_downward")',
            # SVG icons
            'svg[class*="download"]',
            'svg[class*="arrow-down"]',
            # Links e botões com download
            'a[href*="download"]',
            'a[title*="Download"]',
            'button[title*="Download"]',
            # Classes genéricas de download
            '[class*="download-icon"]',
            '[class*="download-btn"]',
            '[class*="btn-download"]'
        ]
        
        all_download_elements = []
        
        for selector in download_icon_selectors:
            try:
                if ':contains(' in selector:
                    # Para seletores com :contains, usar XPath
                    xpath_selector = selector.replace('i[class*="material-icons"]:contains("', '//i[contains(@class, "material-icons") and contains(text(), "').replace('")]', '")]')
                    elements = self.driver.find_elements(By.XPATH, xpath_selector)
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                all_download_elements.extend(elements)
                
                if elements:
                    print(f"   ✅ {selector}: {len(elements)} elementos")
                    
            except Exception as e:
                continue
                
        print(f"📋 Total de possíveis ícones de download: {len(all_download_elements)}")
        
        if not all_download_elements:
            print("❌ Nenhum ícone de download encontrado!")
            print("🔧 Vamos procurar por outros padrões...")
            
            # Busca alternativa por elementos clicáveis próximos a datas
            return self.find_downloads_by_date_proximity()
            
        # Para cada ícone de download, verifica se está próximo a uma data do período
        valid_downloads = []
        
        print(f"\n🔍 Verificando quais ícones estão próximos a datas do período...")
        
        for i, download_elem in enumerate(all_download_elements):
            try:
                print(f"   Analisando ícone {i+1}/{len(all_download_elements)}...")
                
                # Procura por datas próximas a este ícone
                date_found = self.find_date_near_element(download_elem, range_start, range_end)
                
                if date_found:
                    valid_downloads.append({
                        'download_element': download_elem,
                        'date': date_found['date'],
                        'date_str': date_found['date_str'],
                        'date_text': date_found['text'],
                        'proximity': date_found['proximity']
                    })
                    print(f"      ✅ Ícone associado à data: {date_found['date_str']}")
                    
            except Exception as e:
                continue
                
        print(f"\n📋 Ícones de download válidos encontrados: {len(valid_downloads)}")
        
        if valid_downloads:
            print("📄 Downloads disponíveis:")
            for i, item in enumerate(valid_downloads):
                print(f"   {i+1}. {item['date_str']} - {item['date_text'][:60]}...")
                
        return valid_downloads
        
    def find_date_near_element(self, element, range_start, range_end):
        """Procura por datas próximas a um elemento"""
        try:
            # Estratégia: sobe na hierarquia procurando por datas
            current = element
            
            date_patterns = [
                r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b',
                r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})\b'
            ]
            
            month_map = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            
            # Sobe até 20 níveis na hierarquia
            for level in range(20):
                try:
                    text = current.text.strip()
                    
                    if text and len(text) < 500:  # Evita textos muito longos
                        # Procura datas no texto
                        for pattern in date_patterns:
                            matches = re.finditer(pattern, text, re.IGNORECASE)
                            
                            for match in matches:
                                try:
                                    groups = match.groups()
                                    
                                    if len(groups) == 3:
                                        if groups[1] in month_map:  # DD Mon YYYY
                                            day, month_str, year = groups
                                            month = month_map[groups[1]]
                                        elif groups[0] in month_map:  # Mon DD YYYY
                                            month_str, day, year = groups
                                            month = month_map[groups[0]]
                                        else:
                                            continue
                                            
                                        day = int(day)
                                        year = int(year)
                                        doc_date = datetime(year, month, day)
                                        
                                        # Verifica se está no período
                                        if range_start <= doc_date <= range_end:
                                            return {
                                                'date': doc_date,
                                                'date_str': doc_date.strftime('%d %b %Y'),
                                                'text': text,
                                                'proximity': level,
                                                'matched_text': match.group()
                                            }
                                            
                                except (ValueError, KeyError):
                                    continue
                    
                    # Sobe um nível
                    current = current.find_element(By.XPATH, "./..")
                    
                except:
                    break
                    
            return None
            
        except:
            return None
            
    def find_downloads_by_date_proximity(self):
        """Busca alternativa: encontra datas e procura downloads próximos"""
        print("🔍 Estratégia alternativa: procurando por datas primeiro...")
        
        range_start, range_end = self.get_target_date_range()
        
        # Encontra todas as datas na página
        page_text = self.driver.find_element(By.TAG_NAME, "body").text
        
        date_patterns = [
            r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b',
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})\b'
        ]
        
        month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        
        target_date_strings = []
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            
            for match in matches:
                try:
                    groups = match.groups()
                    
                    if len(groups) == 3:
                        if groups[1] in month_map:  # DD Mon YYYY
                            day, month_str, year = groups
                            month = month_map[groups[1]]
                        elif groups[0] in month_map:  # Mon DD YYYY
                            month_str, day, year = groups
                            month = month_map[groups[0]]
                        else:
                            continue
                            
                        day = int(day)
                        year = int(year)
                        doc_date = datetime(year, month, day)
                        
                        # Verifica se está no período
                        if range_start <= doc_date <= range_end:
                            date_str = match.group()
                            if date_str not in [d['date_str'] for d in target_date_strings]:
                                target_date_strings.append({
                                    'date': doc_date,
                                    'date_str': date_str,
                                    'formatted': doc_date.strftime('%d %b %Y')
                                })
                                
                except (ValueError, Exception):
                    continue
                    
        print(f"📅 Datas do período encontradas: {len(target_date_strings)}")
        
        valid_downloads = []
        
        # Para cada data, encontra elementos que a contém e procura downloads próximos
        for date_info in target_date_strings:
            print(f"🔍 Procurando downloads para: {date_info['formatted']}")
            
            # Encontra elementos que contêm essa data
            elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{date_info['date_str']}')]")
            
            for elem in elements:
                download_btn = self.find_download_button_comprehensive(elem)
                if download_btn:
                    valid_downloads.append({
                        'download_element': download_btn,
                        'date': date_info['date'],
                        'date_str': date_info['formatted'],
                        'date_text': elem.text[:100],
                        'proximity': 0
                    })
                    print(f"   ✅ Download encontrado para {date_info['formatted']}")
                    break
                    
        return valid_downloads
        
    def find_download_button_comprehensive(self, element):
        """Busca abrangente por botões de download"""
        try:
            current = element
            
            # Sobe na hierarquia procurando downloads
            for level in range(25):  # Até 25 níveis
                try:
                    # Seletores abrangentes
                    selectors = [
                        './/a[contains(@href, "download") or contains(@href, ".zip") or contains(@href, ".pdf")]',
                        './/button[contains(@class, "download") or contains(@title, "Download")]',
                        './/i[contains(@class, "fa-download") or contains(@class, "fa-arrow-down")]/..',
                        './/i[contains(@class, "download")]/..',
                        './/*[contains(@title, "Download") or contains(@alt, "Download")]',
                        './/*[contains(@onclick, "download")]',
                        './/svg[contains(@class, "download")]/..',
                        # Procura por elementos clicáveis com ícones
                        './/a[.//i or .//svg]',
                        './/button[.//i or .//svg]'
                    ]
                    
                    for selector in selectors:
                        try:
                            download_elem = current.find_element(By.XPATH, selector)
                            
                            # Verifica se parece ser um download
                            href = download_elem.get_attribute('href') or ''
                            title = download_elem.get_attribute('title') or ''
                            onclick = download_elem.get_attribute('onclick') or ''
                            class_attr = download_elem.get_attribute('class') or ''
                            
                            if any(keyword in (href + title + onclick + class_attr).lower() 
                                  for keyword in ['download', 'zip', 'pdf', 'arrow-down']):
                                return download_elem
                                
                        except:
                            continue
                            
                    # Sobe um nível
                    current = current.find_element(By.XPATH, "./..")
                    
                except:
                    break
                    
            return None
            
        except:
            return None
            
    def download_documents(self, valid_downloads):
        """Faz download clicando nos ícones"""
        if not valid_downloads:
            print("❌ Nenhum download válido encontrado")
            return []
            
        print(f"\n📥 Iniciando downloads de {len(valid_downloads)} documentos...")
        
        downloaded_files = []
        
        for i, item in enumerate(valid_downloads):
            try:
                print(f"\n📥 Download {i+1}/{len(valid_downloads)}: {item['date_str']}")
                print(f"   📝 Texto: {item['date_text'][:50]}...")
                
                # Scroll para o elemento
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item['download_element'])
                time.sleep(2)
                
                # Destaca o elemento (para debug visual)
                self.driver.execute_script("arguments[0].style.border='3px solid red';", item['download_element'])
                time.sleep(1)
                
                # Clica no ícone de download
                self.driver.execute_script("arguments[0].click();", item['download_element'])
                print("   🖱️ Clique no ícone executado")
                
                # Remove destaque
                self.driver.execute_script("arguments[0].style.border='';", item['download_element'])
                
                # Aguarda download
                downloaded_file = self.wait_for_download()
                
                if downloaded_file:
                    downloaded_files.append({
                        'file': downloaded_file,
                        'date': item['date'],
                        'date_str': item['date_str']
                    })
                    print(f"   ✅ Baixado: {downloaded_file.name}")
                else:
                    print(f"   ❌ Download falhou")
                    
                time.sleep(4)  # Pausa entre downloads
                
            except Exception as e:
                print(f"   ❌ Erro no download: {e}")
                continue
                
        return downloaded_files
        
    def wait_for_download(self, timeout=90):
        """Aguarda download ser concluído"""
        start_time = time.time()
        initial_files = set(f.name for f in self.download_dir.glob("*"))
        
        print("   ⏳ Aguardando download...")
        
        while time.time() - start_time < timeout:
            current_files = set(f.name for f in self.download_dir.glob("*"))
            new_files = current_files - initial_files
            
            complete_files = []
            for filename in new_files:
                if not filename.endswith('.crdownload'):
                    file_path = self.download_dir / filename
                    if file_path.exists() and file_path.stat().st_size > 0:
                        complete_files.append(filename)
                        
            if complete_files:
                return self.download_dir / complete_files[0]
                
            time.sleep(2)
            
        return None
        
    def extract_pdfs(self, downloaded_files):
        """Extrai PDFs dos arquivos baixados"""
        if not downloaded_files:
            return []
            
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
                                print(f"   📄 PDF extraído: {member}")
                                
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
                
        return extracted_pdfs
        
    def run_downloader(self):
        """Executa o downloader completo"""
        print("🚀 MASTERCARD ICON DOWNLOADER")
        print("=" * 60)
        
        try:
            # Setup
            self.setup_chrome()
            
            # Navegação
            self.open_and_navigate()
            
            # Encontra documentos com ícones
            valid_downloads = self.find_documents_with_download_icons()
            
            if not valid_downloads:
                print("❌ Nenhum ícone de download encontrado para o período")
                return False
                
            # Downloads
            downloaded_files = self.download_documents(valid_downloads)
            
            if not downloaded_files:
                print("❌ Nenhum arquivo foi baixado")
                return False
                
            # Extração
            extracted_pdfs = self.extract_pdfs(downloaded_files)
            
            # Relatório
            range_start, range_end = self.get_target_date_range()
            
            print("\n" + "="*60)
            print("🎉 DOWNLOAD CONCLUÍDO!")
            print(f"📅 Período: {range_start.strftime('%d %b')} - {range_end.strftime('%d %b %Y')}")
            print(f"📋 Ícones encontrados: {len(valid_downloads)}")
            print(f"📥 Arquivos baixados: {len(downloaded_files)}")
            print(f"📄 PDFs extraídos: {len(extracted_pdfs)}")
            
            if extracted_pdfs:
                print(f"\n📁 ARQUIVOS SALVOS EM: {self.pdf_dir.absolute()}")
                for pdf in extracted_pdfs:
                    zip_info = f" (de {pdf['original_zip']})" if pdf['original_zip'] else ""
                    print(f"  • {pdf['pdf_path'].name} ({pdf['date_str']}){zip_info}")
                    
            return len(extracted_pdfs) > 0
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
            
        finally:
            if self.driver:
                input("\nPressione ENTER para fechar o navegador...")
                self.driver.quit()

def main():
    downloader = IconDownloader()
    
    try:
        success = downloader.run_downloader()
        
        if success:
            print("\n🎉 SUCESSO! PDFs baixados com sucesso!")
        else:
            print("\n😔 Nenhum PDF foi baixado")
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo interrompido")

if __name__ == "__main__":
    main()
