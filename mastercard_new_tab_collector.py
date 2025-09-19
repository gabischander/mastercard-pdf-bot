#!/usr/bin/env python3
"""
Mastercard Collector - Corrigido para Nova Aba
Detecta quando uma nova aba é aberta e troca automaticamente
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

class NewTabCollector:
    def __init__(self):
        self.download_dir = Path("downloads_newtab")
        self.pdf_dir = Path("pdfs_newtab")
        self.setup_directories()
        self.driver = None
        self.initial_tabs = []
        
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
        
    def open_and_navigate(self):
        """Abre site e gerencia navegação com nova aba"""
        print("\n🌐 Abrindo mastercardconnect.com...")
        self.driver.get("https://mastercardconnect.com")
        time.sleep(3)
        
        # Armazena as abas iniciais
        self.initial_tabs = self.driver.window_handles
        print(f"📋 Abas iniciais: {len(self.initial_tabs)}")
        
        print("\n" + "="*70)
        print("🎯 NAVEGAÇÃO PASSO A PASSO")
        print("1. Faça login no site")
        print("2. Navegue para: Technical Resource Center")
        print("3. Clique em: Announcements")
        print("   (Isso vai abrir uma NOVA ABA)")
        print("4. NÃO precisa trocar de aba manualmente!")
        print("="*70)
        
        input("Pressione ENTER após clicar em Announcements (nova aba já deve ter aberto)...")
        
        # Detecta nova aba
        self.switch_to_new_tab()
        
    def switch_to_new_tab(self):
        """Detecta e troca para nova aba"""
        print("\n🔄 Detectando nova aba...")
        
        # Aguarda nova aba aparecer
        max_attempts = 10
        for attempt in range(max_attempts):
            current_tabs = self.driver.window_handles
            
            if len(current_tabs) > len(self.initial_tabs):
                # Nova aba detectada!
                new_tabs = [tab for tab in current_tabs if tab not in self.initial_tabs]
                newest_tab = new_tabs[-1]  # Pega a mais recente
                
                print(f"✅ Nova aba detectada! Trocando...")
                self.driver.switch_to.window(newest_tab)
                
                # Aguarda a nova página carregar
                time.sleep(5)
                
                print(f"🔗 Nova URL: {self.driver.current_url}")
                print(f"📄 Novo título: {self.driver.title}")
                
                return True
                
            print(f"⏳ Tentativa {attempt + 1}/{max_attempts} - Aguardando nova aba...")
            time.sleep(2)
            
        print("⚠️ Nova aba não detectada automaticamente")
        
        # Lista todas as abas disponíveis
        all_tabs = self.driver.window_handles
        print(f"📋 Total de abas disponíveis: {len(all_tabs)}")
        
        # Se há mais de uma aba, oferece escolha manual
        if len(all_tabs) > 1:
            print("\n🔧 Seleção manual de aba:")
            
            for i, tab_handle in enumerate(all_tabs):
                self.driver.switch_to.window(tab_handle)
                time.sleep(1)
                print(f"  {i+1}. {self.driver.title[:50]}... - {self.driver.current_url[:60]}...")
                
            choice = input(f"\nEscolha a aba de Announcements (1-{len(all_tabs)}): ")
            
            try:
                tab_index = int(choice) - 1
                if 0 <= tab_index < len(all_tabs):
                    self.driver.switch_to.window(all_tabs[tab_index])
                    print(f"✅ Trocou para aba {choice}")
                    time.sleep(3)
                    return True
                else:
                    print("❌ Número inválido")
            except ValueError:
                print("❌ Entrada inválida")
                
        return False
        
    def find_dates_and_downloads(self):
        """Encontra datas e downloads na página de Announcements"""
        print(f"\n🔍 Analisando página de Announcements...")
        print(f"🔗 URL atual: {self.driver.current_url}")
        
        # Aguarda página carregar completamente
        time.sleep(5)
        
        week_start, week_end = self.get_target_week()
        
        # Procura por elementos com anos (2024, 2025)
        year_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '2025') or contains(text(), '2024')]")
        print(f"📋 Elementos com anos: {len(year_elements)}")
        
        # Padrões de data
        date_patterns = [
            r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})'
        ]
        
        month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        
        found_documents = []
        
        for element in year_elements:
            try:
                text = element.text.strip()
                if not text or len(text) > 400:
                    continue
                    
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
                                
                                # Verifica se está na semana alvo
                                if week_start <= doc_date <= week_end:
                                    print(f"✅ Documento da semana alvo: {doc_date.strftime('%d %b %Y')}")
                                    
                                    # Procura botão de download
                                    download_btn = self.find_download_button(element)
                                    
                                    if download_btn:
                                        found_documents.append({
                                            'date': doc_date,
                                            'date_str': doc_date.strftime('%d %b %Y'),
                                            'element': element,
                                            'download_button': download_btn,
                                            'text': text[:100]
                                        })
                                        print(f"  📥 Download disponível!")
                                    else:
                                        print(f"  ⚠️ Download não encontrado")
                                        
                        except (ValueError, KeyError):
                            continue
                            
            except Exception as e:
                continue
                
        print(f"\n📋 Documentos da semana alvo com download: {len(found_documents)}")
        
        # Se não encontrou nenhum, mostra todas as datas para debug
        if not found_documents:
            print("\n🔧 DEBUG - Todas as datas encontradas:")
            all_dates = []
            
            for element in year_elements[:10]:  # Primeiros 10
                text = element.text.strip()
                if text and len(text) < 200:
                    for pattern in date_patterns:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        for match in matches:
                            if isinstance(match, tuple):
                                date_str = " ".join(match)
                                all_dates.append(f"  • {date_str} - {text[:60]}...")
                                
            for date_info in all_dates[:15]:  # Primeiras 15
                print(date_info)
                
        return found_documents
        
    def find_download_button(self, element):
        """Encontra botão de download próximo ao elemento"""
        try:
            current = element
            
            # Sobe na hierarquia procurando download
            for level in range(10):
                try:
                    selectors = [
                        './/a[contains(@href, "download") or contains(@href, ".zip")]',
                        './/a[contains(@class, "download")]',
                        './/button[contains(@class, "download")]',
                        './/*[contains(@title, "Download") or contains(@alt, "Download")]',
                        './/*[contains(text(), "Download")]'
                    ]
                    
                    for selector in selectors:
                        try:
                            btn = current.find_element(By.XPATH, selector)
                            return btn
                        except:
                            continue
                            
                    # Sobe um nível
                    current = current.find_element(By.XPATH, "./..")
                    
                except:
                    break
                    
            return None
            
        except:
            return None
            
    def download_and_extract(self, documents):
        """Faz download e extrai PDFs"""
        if not documents:
            return []
            
        print(f"\n📥 Iniciando downloads de {len(documents)} documentos...")
        
        downloaded_files = []
        
        for i, doc in enumerate(documents):
            try:
                print(f"\n📥 Download {i+1}/{len(documents)}: {doc['date_str']}")
                
                # Scroll e clique
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", doc['download_button'])
                time.sleep(2)
                self.driver.execute_script("arguments[0].click();", doc['download_button'])
                
                # Aguarda download
                downloaded_file = self.wait_for_download()
                
                if downloaded_file:
                    downloaded_files.append({
                        'file': downloaded_file,
                        'date': doc['date'],
                        'date_str': doc['date_str']
                    })
                    print(f"  ✅ Baixado: {downloaded_file.name}")
                    
                time.sleep(3)
                
            except Exception as e:
                print(f"  ❌ Erro: {e}")
                continue
                
        # Extrai PDFs
        extracted_pdfs = []
        
        for file_info in downloaded_files:
            file_path = file_info['file']
            
            try:
                if file_path.suffix.lower() == '.zip':
                    print(f"📦 Extraindo: {file_path.name}")
                    
                    extract_dir = self.pdf_dir / f"extracted_{file_info['date_str'].replace(' ', '_')}"
                    extract_dir.mkdir(exist_ok=True)
                    
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        for member in zip_ref.namelist():
                            if member.lower().endswith('.pdf'):
                                zip_ref.extract(member, extract_dir)
                                extracted_pdf = extract_dir / member
                                extracted_pdfs.append({
                                    'pdf_path': extracted_pdf,
                                    'date_str': file_info['date_str']
                                })
                                print(f"  📄 PDF: {member}")
                                
                elif file_path.suffix.lower() == '.pdf':
                    pdf_dest = self.pdf_dir / file_path.name
                    shutil.copy2(file_path, pdf_dest)
                    extracted_pdfs.append({
                        'pdf_path': pdf_dest,
                        'date_str': file_info['date_str']
                    })
                    
            except Exception as e:
                print(f"❌ Erro ao extrair {file_path}: {e}")
                
        return extracted_pdfs
        
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
        
    def run_collection(self):
        """Executa coleta completa"""
        print("🚀 MASTERCARD NEW TAB COLLECTOR")
        print("=" * 60)
        
        try:
            week_start, week_end = self.get_target_week()
            self.setup_chrome()
            
            # Navegação com detecção de nova aba
            self.open_and_navigate()
            
            # Busca documentos
            documents = self.find_dates_and_downloads()
            
            if not documents:
                print("❌ Nenhum documento da semana alvo encontrado")
                return False
                
            # Download e extração
            extracted_pdfs = self.download_and_extract(documents)
            
            # Relatório
            print("\n" + "="*60)
            print("✅ COLETA CONCLUÍDA!")
            print(f"📅 Período: {week_start.strftime('%d %b')} - {week_end.strftime('%d %b %Y')}")
            print(f"📋 Documentos: {len(documents)}")
            print(f"📄 PDFs extraídos: {len(extracted_pdfs)}")
            
            if extracted_pdfs:
                print("\n📁 ARQUIVOS:")
                for pdf in extracted_pdfs:
                    print(f"  • {pdf['pdf_path'].name} ({pdf['date_str']})")
                    
            return True
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
            
        finally:
            if self.driver:
                input("\nPressione ENTER para fechar...")
                self.driver.quit()

def main():
    collector = NewTabCollector()
    
    try:
        success = collector.run_collection()
        
        if success:
            print("\n🎉 SUCESSO! Verifique 'pdfs_newtab'")
        else:
            print("\n❌ FALHOU")
            
    except KeyboardInterrupt:
        print("\n⏹️ Interrompido")

if __name__ == "__main__":
    main()
