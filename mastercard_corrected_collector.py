#!/usr/bin/env python3
"""
Mastercard Corrected Collector
Período: Da quarta-feira anterior até o dia corrente
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

class CorrectedCollector:
    def __init__(self):
        self.download_dir = Path("downloads_corrected")
        self.pdf_dir = Path("pdfs_corrected")
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
        
    def get_correct_date_range(self):
        """Calcula da quarta-feira anterior até hoje"""
        today = datetime.now()
        
        # Encontra a quarta-feira anterior
        # Quarta-feira = weekday() 2
        days_since_wednesday = (today.weekday() - 2) % 7
        if days_since_wednesday == 0 and today.weekday() == 2:
            # Se hoje é quarta, pega a quarta anterior (7 dias atrás)
            last_wednesday = today - timedelta(days=7)
        else:
            # Senão, pega a quarta mais recente
            last_wednesday = today - timedelta(days=days_since_wednesday)
            
        # Se a "quarta anterior" for no futuro, pega a de uma semana antes
        if last_wednesday > today:
            last_wednesday = last_wednesday - timedelta(days=7)
            
        print(f"🗓️ Hoje: {today.strftime('%d %b %Y (%A)')}")
        print(f"🎯 Período: {last_wednesday.strftime('%d %b %Y (%A)')} até {today.strftime('%d %b %Y (%A)')}")
        print(f"📅 Datas específicas do período:")
        
        current_date = last_wednesday
        dates_in_range = []
        
        while current_date <= today:
            dates_in_range.append(current_date)
            print(f"   • {current_date.strftime('%A, %d %b %Y')}")
            current_date += timedelta(days=1)
            
        return last_wednesday, today, dates_in_range
        
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
        """Abre site e aguarda navegação completa"""
        print("\n🌐 Abrindo mastercardconnect.com...")
        self.driver.get("https://mastercardconnect.com")
        time.sleep(3)
        
        range_start, range_end, dates_list = self.get_correct_date_range()
        
        print("\n" + "="*80)
        print("🎯 FAÇA A NAVEGAÇÃO COMPLETA MANUALMENTE")
        print("")
        print("1. 🔑 Faça login no site")
        print("2. 🏢 Clique em 'Technical Resource Center'")
        print("3. 📢 Clique em 'Announcements' (nova aba vai abrir)")
        print("4. ⏳ Aguarde a página carregar COMPLETAMENTE")
        print("5. 👀 Certifique-se de que vê os documentos com datas")
        print("")
        print(f"🎯 PROCURE POR DOCUMENTOS COM PUBLICATION DATE ENTRE:")
        print(f"   📅 {range_start.strftime('%d %b %Y')} e {range_end.strftime('%d %b %Y')}")
        print("")
        print("💡 DICA: Role a página para ver se há mais documentos!")
        print("="*80)
        
        # Aguarda confirmação
        input("\nPressione ENTER quando estiver vendo os documentos com Publication Date...")
        
        # Gerencia abas
        all_tabs = self.driver.window_handles
        
        if len(all_tabs) > 1:
            print(f"\n📋 Detectadas {len(all_tabs)} abas abertas")
            
            for i, tab_handle in enumerate(all_tabs):
                original_tab = self.driver.current_window_handle
                self.driver.switch_to.window(tab_handle)
                time.sleep(1)
                title = self.driver.title[:50]
                url = self.driver.current_url[:70]
                print(f"  {i+1}. {title}... - {url}...")
                
            # Volta para a aba original
            self.driver.switch_to.window(original_tab)
            
            choice = input(f"\nQual aba tem os Announcements? (1-{len(all_tabs)}): ")
            
            try:
                tab_index = int(choice) - 1
                if 0 <= tab_index < len(all_tabs):
                    self.driver.switch_to.window(all_tabs[tab_index])
                    print(f"✅ Trocou para aba {choice}")
                    time.sleep(2)
            except ValueError:
                print("❌ Entrada inválida, usando aba atual")
                
    def scan_for_target_documents(self):
        """Escaneia documentos no período correto"""
        print(f"\n🔍 Escaneando página para documentos...")
        print(f"🔗 URL atual: {self.driver.current_url}")
        print(f"📄 Título: {self.driver.title}")
        
        range_start, range_end, dates_in_range = self.get_correct_date_range()
        
        # Aguarda carregamento
        print("⏳ Aguardando carregamento completo...")
        time.sleep(8)
        
        found_documents = []
        
        # Estratégia 1: Procura por texto "Publication Date"
        print("\n🔍 Estratégia 1: Procurando por texto 'Publication Date'")
        pub_date_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Publication Date') or contains(text(), 'Publication date')]")
        print(f"   Encontrados: {len(pub_date_elements)} elementos")
        
        for elem in pub_date_elements:
            doc = self.extract_date_from_element(elem, range_start, range_end)
            if doc:
                found_documents.append(doc)
                
        # Estratégia 2: Busca por padrões de data no período
        print(f"\n🔍 Estratégia 2: Procurando por datas no período")
        
        date_patterns = [
            r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b',
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})\b'
        ]
        
        month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        
        # Pega todo o texto da página
        page_text = self.driver.find_element(By.TAG_NAME, "body").text
        
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
                        
                        # Verifica se está no período correto
                        if range_start <= doc_date <= range_end:
                            print(f"   ✅ Data no período: {doc_date.strftime('%d %b %Y')}")
                            
                            # Procura elemento específico com essa data
                            date_str = match.group()
                            elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{date_str}')]")
                            
                            for elem in elements:
                                download_btn = self.find_download_button_near(elem)
                                if download_btn:
                                    # Verifica se já não temos este documento
                                    if not any(d['date'] == doc_date and d['text'][:50] == elem.text[:50] for d in found_documents):
                                        found_documents.append({
                                            'date': doc_date,
                                            'date_str': doc_date.strftime('%d %b %Y'),
                                            'element': elem,
                                            'download_button': download_btn,
                                            'text': elem.text[:150],
                                            'matched_date': date_str
                                        })
                                    break
                                    
                except (ValueError, Exception):
                    continue
                    
        # Remove duplicatas mais rigorosamente
        unique_docs = {}
        for doc in found_documents:
            key = f"{doc['date_str']}-{doc['text'][:80]}"
            if key not in unique_docs:
                unique_docs[key] = doc
                
        found_documents = list(unique_docs.values())
        
        print(f"\n📋 Total de documentos no período encontrados: {len(found_documents)}")
        
        if found_documents:
            print("📄 Documentos encontrados:")
            for i, doc in enumerate(found_documents):
                print(f"   {i+1}. {doc['date_str']} - {doc['text'][:80]}...")
        else:
            print("❌ Nenhum documento no período encontrado")
            print("\n🔧 MODO DEBUG - Todas as datas na página:")
            
            all_dates = []
            for pattern in date_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        date_str = " ".join(match)
                        all_dates.append(date_str)
                        
            unique_dates = list(set(all_dates))
            unique_dates.sort()
            
            print(f"📅 Primeiras 25 datas encontradas:")
            for i, date_str in enumerate(unique_dates[:25]):
                print(f"   {i+1}. {date_str}")
                
            if len(unique_dates) > 25:
                print(f"   ... e mais {len(unique_dates) - 25} datas")
                
        return found_documents
        
    def extract_date_from_element(self, element, range_start, range_end):
        """Extrai data de um elemento específico"""
        try:
            text = element.text.strip()
            
            patterns = [
                r'Publication Date:\s*(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})',
                r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})'
            ]
            
            month_map = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        day, month_str, year = match.groups()
                        month = month_map[month_str]
                        doc_date = datetime(int(year), month, int(day))
                        
                        # Verifica se está no período correto
                        if range_start <= doc_date <= range_end:
                            download_btn = self.find_download_button_near(element)
                            if download_btn:
                                return {
                                    'date': doc_date,
                                    'date_str': doc_date.strftime('%d %b %Y'),
                                    'element': element,
                                    'download_button': download_btn,
                                    'text': text[:150],
                                    'matched_date': match.group()
                                }
                    except (ValueError, KeyError):
                        continue
                        
            return None
            
        except Exception:
            return None
            
    def find_download_button_near(self, element):
        """Encontra botão de download próximo"""
        try:
            current = element
            
            # Sobe na hierarquia
            for level in range(15):
                try:
                    selectors = [
                        './/a[contains(@href, "download") or contains(@href, ".zip") or contains(@href, ".pdf")]',
                        './/button[contains(@class, "download") or contains(@title, "Download")]',
                        './/a[contains(@class, "download") or contains(@title, "Download")]',
                        './/i[contains(@class, "download") or contains(@class, "arrow-down")]/..',
                        './/*[contains(@title, "Download") or contains(@alt, "Download")]',
                        './/*[contains(text(), "Download") or contains(text(), "⬇")]'
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
            
    def download_and_process(self, documents):
        """Faz download e processa arquivos"""
        if not documents:
            return []
            
        print(f"\n📥 Iniciando downloads de {len(documents)} documentos...")
        
        downloaded_files = []
        
        for i, doc in enumerate(documents):
            try:
                print(f"\n📥 Download {i+1}/{len(documents)}: {doc['date_str']}")
                print(f"   📝 Documento: {doc['text'][:60]}...")
                
                # Scroll para o botão
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", doc['download_button'])
                time.sleep(2)
                
                # Clica
                self.driver.execute_script("arguments[0].click();", doc['download_button'])
                print("   🖱️ Clique executado")
                
                # Aguarda download
                downloaded_file = self.wait_for_download(timeout=90)
                
                if downloaded_file:
                    downloaded_files.append({
                        'file': downloaded_file,
                        'date': doc['date'],
                        'date_str': doc['date_str']
                    })
                    print(f"   ✅ Baixado: {downloaded_file.name}")
                else:
                    print(f"   ❌ Download falhou (timeout)")
                    
                time.sleep(4)  # Pausa entre downloads
                
            except Exception as e:
                print(f"   ❌ Erro no download: {e}")
                continue
                
        print(f"\n📥 Downloads concluídos: {len(downloaded_files)} de {len(documents)}")
        
        # Processa/extrai arquivos
        return self.extract_and_organize(downloaded_files)
        
    def wait_for_download(self, timeout=90):
        """Aguarda download"""
        start_time = time.time()
        initial_files = set(f.name for f in self.download_dir.glob("*"))
        
        print("   ⏳ Aguardando download...")
        
        while time.time() - start_time < timeout:
            current_files = set(f.name for f in self.download_dir.glob("*"))
            new_files = current_files - initial_files
            
            # Verifica arquivos completos
            complete_files = []
            for filename in new_files:
                if not filename.endswith('.crdownload'):
                    file_path = self.download_dir / filename
                    if file_path.exists() and file_path.stat().st_size > 0:
                        complete_files.append(filename)
                        
            if complete_files:
                return self.download_dir / complete_files[0]
                
            time.sleep(3)
            
        return None
        
    def extract_and_organize(self, downloaded_files):
        """Extrai e organiza PDFs"""
        print(f"\n📂 Processando {len(downloaded_files)} arquivos baixados...")
        
        extracted_pdfs = []
        
        for file_info in downloaded_files:
            file_path = file_info['file']
            
            try:
                if file_path.suffix.lower() == '.zip':
                    print(f"📦 Extraindo ZIP: {file_path.name}")
                    
                    extract_dir = self.pdf_dir / f"extracted_{file_info['date_str'].replace(' ', '_')}"
                    extract_dir.mkdir(exist_ok=True)
                    
                    pdf_count = 0
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
                                pdf_count += 1
                                print(f"   📄 PDF extraído: {member}")
                                
                    print(f"   ✅ {pdf_count} PDFs extraídos de {file_path.name}")
                    
                elif file_path.suffix.lower() == '.pdf':
                    # Já é PDF
                    pdf_dest = self.pdf_dir / file_path.name
                    shutil.copy2(file_path, pdf_dest)
                    extracted_pdfs.append({
                        'pdf_path': pdf_dest,
                        'date_str': file_info['date_str'],
                        'original_zip': None
                    })
                    print(f"📄 PDF copiado: {file_path.name}")
                    
            except Exception as e:
                print(f"❌ Erro ao processar {file_path}: {e}")
                continue
                
        print(f"📂 Total de PDFs extraídos: {len(extracted_pdfs)}")
        return extracted_pdfs
        
    def run_collection(self):
        """Executa coleta completa"""
        print("🚀 MASTERCARD CORRECTED COLLECTOR")
        print("=" * 70)
        
        try:
            # Setup
            range_start, range_end, dates_list = self.get_correct_date_range()
            self.setup_chrome()
            
            # Navegação manual
            self.open_and_navigate()
            
            # Escaneia documentos
            documents = self.scan_for_target_documents()
            
            if not documents:
                print("\n❌ Nenhum documento no período encontrado")
                choice = input("Deseja continuar mesmo assim? (s/n): ")
                if choice.lower() != 's':
                    return False
                    
            # Download e processamento
            extracted_pdfs = self.download_and_process(documents)
            
            # Relatório final
            print("\n" + "="*70)
            print("🎉 COLETA FINALIZADA!")
            print(f"📅 Período: {range_start.strftime('%d %b')} - {range_end.strftime('%d %b %Y')}")
            print(f"📋 Documentos encontrados: {len(documents)}")
            print(f"📥 Arquivos baixados: {len([f for f in extracted_pdfs if f])}")
            print(f"📄 PDFs extraídos: {len(extracted_pdfs)}")
            
            if extracted_pdfs:
                print(f"\n📁 ARQUIVOS COLETADOS (pasta: {self.pdf_dir}):")
                for pdf in extracted_pdfs:
                    zip_info = f" (de {pdf['original_zip']})" if pdf['original_zip'] else ""
                    print(f"  • {pdf['pdf_path'].name} ({pdf['date_str']}){zip_info}")
                    
                print(f"\n💡 Os PDFs estão salvos em: {self.pdf_dir.absolute()}")
            else:
                print("\n📁 Nenhum PDF foi extraído")
                
            return len(extracted_pdfs) > 0
            
        except Exception as e:
            print(f"❌ Erro durante coleta: {e}")
            return False
            
        finally:
            if self.driver:
                input("\nPressione ENTER para fechar o navegador...")
                self.driver.quit()

def main():
    collector = CorrectedCollector()
    
    try:
        success = collector.run_collection()
        
        if success:
            print("\n🎉 SUCESSO! PDFs coletados com sucesso!")
        else:
            print("\n😔 Nenhum PDF foi coletado")
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo interrompido pelo usuário")

if __name__ == "__main__":
    main()
