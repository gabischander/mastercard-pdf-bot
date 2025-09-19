#!/usr/bin/env python3
"""
Mastercard Precise Downloader
Clica especificamente no ícone de seta para baixo no canto direito de cada documento
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
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

class PreciseDownloader:
    def __init__(self):
        self.download_dir = Path("downloads_precise")
        self.pdf_dir = Path("pdfs_precise")
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
        
    def navigate_to_announcements(self):
        """Navega para announcements"""
        print("\n🌐 Abrindo mastercardconnect.com...")
        self.driver.get("https://mastercardconnect.com")
        time.sleep(3)
        
        range_start, range_end = self.get_target_date_range()
        
        print(f"\n🎯 DOCUMENTOS A BAIXAR: {range_start.strftime('%d %b')} - {range_end.strftime('%d %b %Y')}")
        print("="*60)
        print("1. 🔑 Faça login")
        print("2. 🏢 Vá para Technical Resource Center")  
        print("3. 📢 Clique em Announcements")
        print("4. 👀 Aguarde ver os documentos")
        print("="*60)
        
        input("Pressione ENTER quando estiver vendo os documentos...")
        
        # Gerencia abas
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            print("✅ Usando última aba")
            
        time.sleep(5)  # Aguarda carregamento
        
    def find_document_containers(self):
        """Encontra containers de documentos com Publication Date no período"""
        print(f"\n🔍 Procurando documentos no período...")
        
        range_start, range_end = self.get_target_date_range()
        
        # Estratégia: procurar por elementos que contêm "Publication Date:"
        pub_date_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Publication Date:')]")
        print(f"📋 Elementos com 'Publication Date:': {len(pub_date_elements)}")
        
        valid_documents = []
        
        for i, pub_date_elem in enumerate(pub_date_elements):
            try:
                # Pega o texto completo do elemento
                date_text = pub_date_elem.text.strip()
                print(f"\n📅 Analisando: {date_text}")
                
                # Extrai a data do texto
                date_match = re.search(r'Publication Date:\s*(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})', date_text)
                
                if date_match:
                    day, month_str, year = date_match.groups()
                    
                    month_map = {
                        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                    }
                    
                    if month_str in month_map:
                        doc_date = datetime(int(year), month_map[month_str], int(day))
                        
                        # Verifica se está no período
                        if range_start <= doc_date <= range_end:
                            print(f"   ✅ Data {doc_date.strftime('%d %b %Y')} está no período!")
                            
                            # Encontra o container pai do documento
                            container = self.find_document_container(pub_date_elem)
                            
                            if container:
                                # Procura o ícone de download neste container
                                download_icon = self.find_download_icon_in_container(container)
                                
                                if download_icon:
                                    valid_documents.append({
                                        'container': container,
                                        'download_icon': download_icon,
                                        'date': doc_date,
                                        'date_str': doc_date.strftime('%d %b %Y'),
                                        'title': self.get_document_title(container)
                                    })
                                    print(f"   🎯 Ícone de download encontrado!")
                                else:
                                    print(f"   ❌ Ícone de download não encontrado")
                            else:
                                print(f"   ❌ Container do documento não encontrado")
                        else:
                            print(f"   ⏭️ Data {doc_date.strftime('%d %b %Y')} fora do período")
                            
            except Exception as e:
                print(f"   ❌ Erro ao processar: {e}")
                continue
                
        print(f"\n📋 Documentos válidos encontrados: {len(valid_documents)}")
        
        if valid_documents:
            print("📄 Lista de downloads:")
            for i, doc in enumerate(valid_documents):
                print(f"   {i+1}. {doc['title'][:60]}... ({doc['date_str']})")
                
        return valid_documents
        
    def find_document_container(self, pub_date_element):
        """Encontra o container principal do documento"""
        current = pub_date_element
        
        # Sobe na hierarquia até encontrar um container que parece ser o documento completo
        for level in range(15):
            try:
                parent = current.find_element(By.XPATH, "./..")
                
                # Verifica se este container tem características de um documento completo
                if self.is_document_container(parent):
                    return parent
                    
                current = parent
                
            except:
                break
                
        return None
        
    def is_document_container(self, element):
        """Verifica se um elemento é um container de documento"""
        try:
            # Procura por indicadores de que é um container completo
            text = element.text
            
            # Deve ter título, publication date, e ser um container substancial
            has_title = len(text.split('\n')) > 3  # Múltiplas linhas
            has_pub_date = 'Publication Date:' in text
            has_content = len(text) > 100  # Conteúdo substancial
            
            # Verifica tag e classes
            tag = element.tag_name.lower()
            classes = element.get_attribute('class') or ''
            
            # Tags típicas de containers
            is_container_tag = tag in ['div', 'article', 'section', 'li']
            
            return has_title and has_pub_date and has_content and is_container_tag
            
        except:
            return False
            
    def find_download_icon_in_container(self, container):
        """Procura o ícone de download específico dentro do container"""
        
        # Estratégias para encontrar o ícone de download (seta para baixo)
        download_selectors = [
            # Ícones Font Awesome
            './/i[contains(@class, "fa-download")]',
            './/i[contains(@class, "fa-arrow-down")]',
            './/i[contains(@class, "download")]',
            
            # SVG ícones
            './/svg[contains(@class, "download")]',
            './/svg[*//path[contains(@d, "download") or contains(@d, "arrow")]]',
            
            # Links e botões com download
            './/a[contains(@href, "download") or contains(@title, "Download") or contains(@aria-label, "Download")]',
            './/button[contains(@title, "Download") or contains(@aria-label, "Download")]',
            
            # Elementos genéricos com classes de download
            './/*[contains(@class, "download")]',
            './/*[contains(@class, "btn-download")]',
            './/*[contains(@class, "download-btn")]',
            './/*[contains(@class, "download-icon")]',
            
            # Procura por elementos clicáveis no canto superior direito
            './/*[@onclick]',
            './/a',
            './/button'
        ]
        
        for selector in download_selectors:
            try:
                elements = container.find_elements(By.XPATH, selector)
                
                for elem in elements:
                    # Verifica se parece ser um ícone de download
                    if self.is_download_icon(elem, container):
                        return elem
                        
            except:
                continue
                
        return None
        
    def is_download_icon(self, element, container):
        """Verifica se um elemento é o ícone de download"""
        try:
            # Atributos do elemento
            href = element.get_attribute('href') or ''
            onclick = element.get_attribute('onclick') or ''
            title = element.get_attribute('title') or ''
            aria_label = element.get_attribute('aria-label') or ''
            classes = element.get_attribute('class') or ''
            
            # Texto e HTML interno
            text = element.text.strip().lower()
            inner_html = element.get_attribute('innerHTML') or ''
            
            # Palavras-chave de download
            download_keywords = ['download', 'zip', 'pdf', 'file', 'arrow-down', 'export']
            
            # Verifica se contém palavras-chave de download
            all_text = f"{href} {onclick} {title} {aria_label} {classes} {text} {inner_html}".lower()
            has_download_keyword = any(keyword in all_text for keyword in download_keywords)
            
            # Verifica posição (deve estar no lado direito)
            try:
                elem_rect = element.rect
                container_rect = container.rect
                
                # Deve estar na metade direita do container
                container_right_half = container_rect['x'] + (container_rect['width'] * 0.6)
                is_on_right = elem_rect['x'] >= container_right_half
                
            except:
                is_on_right = True  # Se não conseguir verificar posição, assume que sim
                
            # Deve ser clicável
            is_clickable = element.tag_name.lower() in ['a', 'button'] or onclick or href
            
            return has_download_keyword and is_on_right and is_clickable
            
        except:
            return False
            
    def get_document_title(self, container):
        """Extrai o título do documento"""
        try:
            # Procura por elementos que parecem ser títulos
            title_candidates = container.find_elements(By.XPATH, 
                './/h1 | .//h2 | .//h3 | .//h4 | .//h5 | .//h6 | .//*[contains(@class, "title")] | .//*[contains(@class, "heading")]')
            
            if title_candidates:
                return title_candidates[0].text.strip()
                
            # Se não encontrar, pega as primeiras linhas do texto
            lines = container.text.strip().split('\n')
            for line in lines:
                if len(line) > 20 and not line.startswith('Audience:') and not line.startswith('Publication Date:'):
                    return line.strip()
                    
            return "Documento sem título"
            
        except:
            return "Documento sem título"
            
    def download_documents(self, documents):
        """Executa downloads clicando nos ícones"""
        if not documents:
            print("❌ Nenhum documento para baixar")
            return []
            
        print(f"\n📥 Iniciando downloads de {len(documents)} documentos...")
        
        downloaded_files = []
        actions = ActionChains(self.driver)
        
        for i, doc in enumerate(documents):
            try:
                print(f"\n📥 Download {i+1}/{len(documents)}: {doc['title'][:50]}...")
                print(f"   📅 Data: {doc['date_str']}")
                
                # Scroll para o documento
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", doc['container'])
                time.sleep(2)
                
                # Destaca o ícone de download (para debug visual)
                self.driver.execute_script("arguments[0].style.border='3px solid red';", doc['download_icon'])
                time.sleep(1)
                
                print("   🖱️ Clicando no ícone de download...")
                
                # Tenta diferentes métodos de clique
                try:
                    # Método 1: Clique direto
                    doc['download_icon'].click()
                except:
                    try:
                        # Método 2: JavaScript click
                        self.driver.execute_script("arguments[0].click();", doc['download_icon'])
                    except:
                        # Método 3: ActionChains
                        actions.move_to_element(doc['download_icon']).click().perform()
                
                # Remove destaque
                self.driver.execute_script("arguments[0].style.border='';", doc['download_icon'])
                
                print("   ⏳ Aguardando download...")
                
                # Aguarda download
                downloaded_file = self.wait_for_download()
                
                if downloaded_file:
                    downloaded_files.append({
                        'file': downloaded_file,
                        'date': doc['date'],
                        'date_str': doc['date_str'],
                        'title': doc['title']
                    })
                    print(f"   ✅ Baixado: {downloaded_file.name}")
                else:
                    print(f"   ❌ Download falhou ou não detectado")
                    
                time.sleep(3)  # Pausa entre downloads
                
            except Exception as e:
                print(f"   ❌ Erro no download: {e}")
                continue
                
        return downloaded_files
        
    def wait_for_download(self, timeout=60):
        """Aguarda download ser concluído"""
        start_time = time.time()
        initial_files = set(f.name for f in self.download_dir.glob("*") if f.is_file())
        
        while time.time() - start_time < timeout:
            current_files = set(f.name for f in self.download_dir.glob("*") if f.is_file())
            new_files = current_files - initial_files
            
            # Verifica arquivos completos (não .crdownload)
            complete_files = []
            for filename in new_files:
                if not filename.endswith('.crdownload') and not filename.endswith('.tmp'):
                    file_path = self.download_dir / filename
                    if file_path.exists() and file_path.stat().st_size > 1000:  # Pelo menos 1KB
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
                                    'title': file_info['title'],
                                    'original_zip': file_path.name
                                })
                                print(f"   📄 PDF extraído: {member}")
                                
                elif file_path.suffix.lower() == '.pdf':
                    pdf_dest = self.pdf_dir / file_path.name
                    shutil.copy2(file_path, pdf_dest)
                    extracted_pdfs.append({
                        'pdf_path': pdf_dest,
                        'date_str': file_info['date_str'],
                        'title': file_info['title'],
                        'original_zip': None
                    })
                    print(f"📄 PDF copiado: {file_path.name}")
                    
            except Exception as e:
                print(f"❌ Erro ao extrair {file_path}: {e}")
                continue
                
        return extracted_pdfs
        
    def run(self):
        """Executa o downloader completo"""
        print("🎯 MASTERCARD PRECISE DOWNLOADER")
        print("=" * 60)
        
        try:
            # Setup
            self.setup_chrome()
            
            # Navegação
            self.navigate_to_announcements()
            
            # Encontra documentos
            documents = self.find_document_containers()
            
            if not documents:
                print("❌ Nenhum documento encontrado no período")
                return False
                
            # Downloads
            downloaded_files = self.download_documents(documents)
            
            if not downloaded_files:
                print("❌ Nenhum arquivo foi baixado")
                return False
                
            # Extração
            extracted_pdfs = self.extract_pdfs(downloaded_files)
            
            # Relatório final
            range_start, range_end = self.get_target_date_range()
            
            print("\n" + "="*60)
            print("🎉 DOWNLOAD CONCLUÍDO!")
            print(f"📅 Período: {range_start.strftime('%d %b')} - {range_end.strftime('%d %b %Y')}")
            print(f"📋 Documentos encontrados: {len(documents)}")
            print(f"📥 Arquivos baixados: {len(downloaded_files)}")
            print(f"📄 PDFs extraídos: {len(extracted_pdfs)}")
            
            if extracted_pdfs:
                print(f"\n📁 ARQUIVOS SALVOS EM: {self.pdf_dir.absolute()}")
                for pdf in extracted_pdfs:
                    zip_info = f" (de {pdf['original_zip']})" if pdf['original_zip'] else ""
                    print(f"  • {pdf['pdf_path'].name}{zip_info}")
                    print(f"    📄 {pdf['title'][:50]}... ({pdf['date_str']})")
                    
            return len(extracted_pdfs) > 0
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
            
        finally:
            if self.driver:
                input("\nPressione ENTER para fechar o navegador...")
                self.driver.quit()

def main():
    downloader = PreciseDownloader()
    
    try:
        success = downloader.run()
        
        if success:
            print("\n🎉 SUCESSO! PDFs baixados com sucesso!")
        else:
            print("\n😔 Nenhum PDF foi baixado")
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo interrompido")

if __name__ == "__main__":
    main()
