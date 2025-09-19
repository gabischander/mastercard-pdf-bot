#!/usr/bin/env python3
"""
Mastercard Fixed Downloader
Procura por "Publication Date" e datas em elementos separados
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
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

class FixedDownloader:
    def __init__(self):
        self.download_dir = Path("downloads_fixed")
        self.pdf_dir = Path("pdfs_fixed")
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
            
        time.sleep(8)  # Aguarda carregamento mais tempo
        
    def find_document_containers_by_date(self):
        """Encontra containers procurando por datas específicas primeiro"""
        print(f"\n🔍 Procurando documentos por datas específicas...")
        
        range_start, range_end = self.get_target_date_range()
        
        # Lista de datas específicas para procurar (baseado no debug)
        target_dates = ['1 Jul 2025', '30 Jun 2025', '25 Jun 2025']
        
        valid_documents = []
        
        for date_str in target_dates:
            print(f"\n📅 Procurando por: {date_str}")
            
            # Converte string para datetime para verificar se está no período
            try:
                date_parts = date_str.split()
                day = int(date_parts[0])
                month_str = date_parts[1]
                year = int(date_parts[2])
                
                month_map = {
                    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                }
                
                if month_str in month_map:
                    doc_date = datetime(year, month_map[month_str], day)
                    
                    # Verifica se está no período
                    if range_start <= doc_date <= range_end:
                        print(f"   ✅ Data {date_str} está no período!")
                        
                        # Procura elementos que contêm essa data
                        date_elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{date_str}')]")
                        print(f"   📋 Elementos com a data: {len(date_elements)}")
                        
                        for i, date_elem in enumerate(date_elements):
                            print(f"      📅 Elemento {i+1}: {date_elem.text.strip()[:50]}")
                            
                            # Encontra o container pai deste elemento
                            container = self.find_document_container_from_date_element(date_elem)
                            
                            if container:
                                # Procura ícone de download no container
                                download_icon = self.find_download_icon_comprehensive(container)
                                
                                if download_icon:
                                    title = self.get_document_title_from_container(container)
                                    
                                    valid_documents.append({
                                        'container': container,
                                        'download_icon': download_icon,
                                        'date': doc_date,
                                        'date_str': date_str,
                                        'title': title
                                    })
                                    print(f"   🎯 Container com ícone de download encontrado!")
                                    print(f"      📄 Título: {title[:60]}...")
                                else:
                                    print(f"   ❌ Ícone de download não encontrado no container")
                            else:
                                print(f"   ❌ Container pai não encontrado")
                    else:
                        print(f"   ⏭️ Data {date_str} fora do período")
                        
            except Exception as e:
                print(f"   ❌ Erro ao processar data {date_str}: {e}")
                continue
                
        print(f"\n📋 Documentos válidos encontrados: {len(valid_documents)}")
        
        if valid_documents:
            print("📄 Lista de downloads:")
            for i, doc in enumerate(valid_documents):
                print(f"   {i+1}. {doc['title'][:60]}... ({doc['date_str']})")
                
        return valid_documents
        
    def find_document_container_from_date_element(self, date_element):
        """Encontra o container do documento a partir do elemento da data"""
        current = date_element
        
        # Sobe na hierarquia até encontrar um container substancial
        for level in range(20):  # Aumentei o nível de busca
            try:
                parent = current.find_element(By.XPATH, "./..")
                
                # Verifica se é um container de documento
                if self.is_substantial_container(parent):
                    return parent
                    
                current = parent
                
            except:
                break
                
        return None
        
    def is_substantial_container(self, element):
        """Verifica se um elemento é um container substancial (documento completo)"""
        try:
            text = element.text.strip()
            
            # Deve ter conteúdo substancial
            has_content = len(text) > 80
            
            # Deve ter múltiplas linhas
            has_multiple_lines = len(text.split('\n')) >= 4
            
            # Pode conter palavras-chave de documento
            has_doc_keywords = any(keyword in text for keyword in [
                'GLB', 'LAC', 'Mastercard', 'Bulletin', 'announcement', 
                'Publication Date', 'Effective Date', 'Audience'
            ])
            
            # Deve ser um elemento container
            tag = element.tag_name.lower()
            is_container_tag = tag in ['div', 'article', 'section', 'li', 'td']
            
            return has_content and has_multiple_lines and has_doc_keywords and is_container_tag
            
        except:
            return False
            
    def find_download_icon_comprehensive(self, container):
        """Busca abrangente por ícones de download"""
        
        print(f"   🔍 Procurando ícone de download no container...")
        
        # Estratégias múltiplas para encontrar ícones de download
        search_strategies = [
            # 1. Busca por classes e atributos óbvios
            {
                'name': 'Classes de download',
                'selectors': [
                    './/*[contains(@class, "download")]',
                    './/*[contains(@class, "btn-download")]', 
                    './/*[contains(@class, "download-btn")]',
                    './/*[contains(@class, "download-icon")]'
                ]
            },
            
            # 2. Busca por ícones Font Awesome
            {
                'name': 'Ícones Font Awesome',
                'selectors': [
                    './/i[contains(@class, "fa-download")]',
                    './/i[contains(@class, "fa-arrow-down")]',
                    './/i[contains(@class, "fa-file")]'
                ]
            },
            
            # 3. Busca por SVGs
            {
                'name': 'SVG ícones',
                'selectors': [
                    './/svg',
                    './/*[name()="svg"]'
                ]
            },
            
            # 4. Busca por links e botões genéricos
            {
                'name': 'Links e botões',
                'selectors': [
                    './/a',
                    './/button',
                    './/*[@onclick]'
                ]
            },
            
            # 5. Busca por elementos com características visuais de ícone
            {
                'name': 'Elementos pequenos clicáveis',
                'selectors': [
                    './/*[@role="button"]',
                    './/*[@tabindex]',
                    './/*[contains(@style, "cursor")]'
                ]
            }
        ]
        
        all_candidates = []
        
        for strategy in search_strategies:
            print(f"      📋 {strategy['name']}...")
            
            for selector in strategy['selectors']:
                try:
                    elements = container.find_elements(By.XPATH, selector)
                    
                    for elem in elements:
                        # Filtra elementos muito pequenos ou ocultos
                        try:
                            rect = elem.rect
                            is_visible = rect['width'] > 0 and rect['height'] > 0
                            is_reasonable_size = rect['width'] >= 10 and rect['height'] >= 10
                            
                            if is_visible and is_reasonable_size:
                                all_candidates.append(elem)
                                
                        except:
                            all_candidates.append(elem)  # Se não conseguir verificar, inclui
                            
                except:
                    continue
                    
        print(f"      📊 Total de candidatos: {len(all_candidates)}")
        
        # Remove duplicatas
        unique_candidates = []
        for candidate in all_candidates:
            if candidate not in unique_candidates:
                unique_candidates.append(candidate)
                
        print(f"      📊 Candidatos únicos: {len(unique_candidates)}")
        
        # Avalia cada candidato
        best_candidate = None
        best_score = 0
        
        for i, candidate in enumerate(unique_candidates):
            score = self.evaluate_download_candidate(candidate, container)
            
            print(f"         {i+1}. <{candidate.tag_name}> score: {score}")
            
            if score > best_score:
                best_score = score
                best_candidate = candidate
                
        if best_candidate and best_score > 2:  # Score mínimo
            print(f"      ✅ Melhor candidato: <{best_candidate.tag_name}> (score: {best_score})")
            return best_candidate
        else:
            print(f"      ❌ Nenhum candidato válido (melhor score: {best_score})")
            return None
            
    def evaluate_download_candidate(self, element, container):
        """Avalia se um elemento pode ser um ícone de download"""
        score = 0
        
        try:
            # Atributos do elemento
            tag = element.tag_name.lower()
            classes = element.get_attribute('class') or ''
            href = element.get_attribute('href') or ''
            onclick = element.get_attribute('onclick') or ''
            title = element.get_attribute('title') or ''
            aria_label = element.get_attribute('aria-label') or ''
            innerHTML = element.get_attribute('innerHTML') or ''
            
            # Texto combinado para análise
            all_text = f"{classes} {href} {onclick} {title} {aria_label} {innerHTML}".lower()
            
            # 1. Palavras-chave de download (+3 pontos cada)
            download_keywords = ['download', 'zip', 'pdf', 'file', 'export', 'save']
            for keyword in download_keywords:
                if keyword in all_text:
                    score += 3
                    
            # 2. Ícones específicos (+2 pontos cada)
            icon_indicators = ['arrow-down', 'fa-download', 'download-icon', 'btn-download']
            for indicator in icon_indicators:
                if indicator in all_text:
                    score += 2
                    
            # 3. Elementos clicáveis (+1 ponto)
            if tag in ['a', 'button'] or onclick or href:
                score += 1
                
            # 4. SVG ou ícone (+1 ponto)
            if tag in ['svg', 'i'] or 'icon' in classes:
                score += 1
                
            # 5. Posição no container (lado direito) (+1 ponto)
            try:
                elem_rect = element.rect
                container_rect = container.rect
                
                if elem_rect and container_rect:
                    # Verifica se está na metade direita
                    container_center = container_rect['x'] + (container_rect['width'] / 2)
                    is_on_right = elem_rect['x'] >= container_center
                    
                    if is_on_right:
                        score += 1
                        
            except:
                pass
                
            # 6. Tamanho adequado para ícone (+1 ponto)
            try:
                rect = element.rect
                if rect:
                    # Ícones geralmente são pequenos mas não minúsculos
                    width, height = rect['width'], rect['height']
                    if 15 <= width <= 50 and 15 <= height <= 50:
                        score += 1
                        
            except:
                pass
                
        except:
            pass
            
        return score
        
    def get_document_title_from_container(self, container):
        """Extrai título do documento do container"""
        try:
            text_lines = container.text.strip().split('\n')
            
            # Procura pela primeira linha que parece ser um título
            for line in text_lines:
                line = line.strip()
                
                # Pula linhas com metadados
                if any(skip in line for skip in ['Audience:', 'Type:', 'Region:', 'Category:', 'Publication Date:', 'Effective Date:']):
                    continue
                    
                # Procura por linhas com códigos de documento (GLB, LAC, etc.)
                if re.match(r'^[A-Z]{2,4}\s+\d+', line):
                    return line
                    
                # Se for uma linha substancial, usa como título
                if len(line) > 20:
                    return line
                    
            return "Documento sem título identificado"
            
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
                print(f"\n📥 Download {i+1}/{len(documents)}:")
                print(f"   📄 {doc['title'][:60]}...")
                print(f"   📅 Data: {doc['date_str']}")
                
                # Scroll para o documento
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", doc['container'])
                time.sleep(3)
                
                # Destaca o ícone (debug visual)
                self.driver.execute_script("arguments[0].style.border='3px solid red'; arguments[0].style.backgroundColor='yellow';", doc['download_icon'])
                time.sleep(2)
                
                print("   🖱️ Clicando no ícone de download...")
                
                # Múltiplas tentativas de clique
                click_success = False
                
                try:
                    # Método 1: Clique direto
                    doc['download_icon'].click()
                    click_success = True
                    print("      ✅ Clique direto funcionou")
                except Exception as e1:
                    try:
                        # Método 2: JavaScript click
                        self.driver.execute_script("arguments[0].click();", doc['download_icon'])
                        click_success = True
                        print("      ✅ Clique JavaScript funcionou")
                    except Exception as e2:
                        try:
                            # Método 3: ActionChains
                            actions.move_to_element(doc['download_icon']).click().perform()
                            click_success = True
                            print("      ✅ ActionChains funcionou")
                        except Exception as e3:
                            print(f"      ❌ Todos os métodos de clique falharam: {e1}, {e2}, {e3}")
                
                # Remove destaque
                self.driver.execute_script("arguments[0].style.border=''; arguments[0].style.backgroundColor='';", doc['download_icon'])
                
                if click_success:
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
                        print(f"   ⚠️ Download não detectado (pode ter funcionado)")
                        
                time.sleep(4)  # Pausa entre downloads
                
            except Exception as e:
                print(f"   ❌ Erro no download: {e}")
                continue
                
        return downloaded_files
        
    def wait_for_download(self, timeout=45):
        """Aguarda download ser concluído"""
        start_time = time.time()
        initial_files = set(f.name for f in self.download_dir.glob("*") if f.is_file())
        
        while time.time() - start_time < timeout:
            current_files = set(f.name for f in self.download_dir.glob("*") if f.is_file())
            new_files = current_files - initial_files
            
            # Verifica arquivos completos
            complete_files = []
            for filename in new_files:
                if not filename.endswith(('.crdownload', '.tmp', '.part')):
                    file_path = self.download_dir / filename
                    if file_path.exists() and file_path.stat().st_size > 500:  # Pelo menos 500 bytes
                        complete_files.append(filename)
                        
            if complete_files:
                return self.download_dir / complete_files[0]
                
            time.sleep(3)
            
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
        print("🔧 MASTERCARD FIXED DOWNLOADER")
        print("=" * 60)
        
        try:
            # Setup
            self.setup_chrome()
            
            # Navegação
            self.navigate_to_announcements()
            
            # Encontra documentos por data
            documents = self.find_document_containers_by_date()
            
            if not documents:
                print("❌ Nenhum documento encontrado no período")
                
                # Tenta busca alternativa
                print("\n🔄 Tentando busca alternativa...")
                return False
                
            # Downloads
            downloaded_files = self.download_documents(documents)
            
            # Extração (mesmo que não tenha detectado downloads)
            extracted_pdfs = self.extract_pdfs(downloaded_files)
            
            # Verifica se há arquivos na pasta de download mesmo sem detecção
            all_files = list(self.download_dir.glob("*"))
            zip_files = [f for f in all_files if f.suffix.lower() == '.zip']
            pdf_files = [f for f in all_files if f.suffix.lower() == '.pdf']
            
            print(f"\n📁 Arquivos encontrados na pasta de download:")
            print(f"   📦 ZIPs: {len(zip_files)}")
            print(f"   📄 PDFs: {len(pdf_files)}")
            
            # Relatório final
            range_start, range_end = self.get_target_date_range()
            
            print("\n" + "="*60)
            print("🎉 PROCESSO CONCLUÍDO!")
            print(f"📅 Período: {range_start.strftime('%d %b')} - {range_end.strftime('%d %b %Y')}")
            print(f"📋 Documentos encontrados: {len(documents)}")
            print(f"📥 Downloads detectados: {len(downloaded_files)}")
            print(f"📄 PDFs extraídos: {len(extracted_pdfs)}")
            print(f"📁 Arquivos totais baixados: {len(all_files)}")
            
            if extracted_pdfs:
                print(f"\n📁 PDFs SALVOS EM: {self.pdf_dir.absolute()}")
                for pdf in extracted_pdfs:
                    zip_info = f" (de {pdf['original_zip']})" if pdf['original_zip'] else ""
                    print(f"  • {pdf['pdf_path'].name}{zip_info}")
                    
            return len(extracted_pdfs) > 0 or len(all_files) > 0
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
            
        finally:
            if self.driver:
                input("\nPressione ENTER para fechar o navegador...")
                self.driver.quit()

def main():
    downloader = FixedDownloader()
    
    try:
        success = downloader.run()
        
        if success:
            print("\n🎉 PROCESSO FINALIZADO!")
        else:
            print("\n😔 Nenhum arquivo detectado")
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo interrompido")

if __name__ == "__main__":
    main()
