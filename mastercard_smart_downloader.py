#!/usr/bin/env python3
"""
Mastercard Smart Downloader
Procura por elementos com "Jul" e reconstrói o contexto das datas
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

class SmartDownloader:
    def __init__(self):
        self.download_dir = Path("downloads_smart")
        self.pdf_dir = Path("pdfs_smart")
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
            
        time.sleep(8)
        
    def find_document_containers_smart(self):
        """Encontra containers usando busca inteligente por elementos que contêm Jul/Jun"""
        print(f"\n🧠 Busca inteligente por documentos...")
        
        range_start, range_end = self.get_target_date_range()
        
        # Estratégia: procurar por elementos que contêm "Jul" ou "Jun"
        month_selectors = [
            "//*[contains(text(), 'Jul')]",
            "//*[contains(text(), 'Jun')]"
        ]
        
        all_month_elements = []
        
        for selector in month_selectors:
            elements = self.driver.find_elements(By.XPATH, selector)
            all_month_elements.extend(elements)
            
        print(f"📋 Elementos com Jul/Jun: {len(all_month_elements)}")
        
        valid_documents = []
        
        for i, month_elem in enumerate(all_month_elements):
            try:
                print(f"\n📅 Analisando elemento {i+1}/{len(all_month_elements)}:")
                
                # Analisa o contexto deste elemento
                date_info = self.extract_date_from_context(month_elem)
                
                if date_info:
                    print(f"   📅 Data encontrada: {date_info['date_str']}")
                    
                    # Verifica se está no período
                    if range_start <= date_info['date'] <= range_end:
                        print(f"   ✅ Data está no período!")
                        
                        # Encontra container do documento
                        container = self.find_document_container_smart(month_elem)
                        
                        if container:
                            # Procura ícone de download
                            download_icon = self.find_download_icon_in_container_smart(container)
                            
                            if download_icon:
                                title = self.get_document_title_smart(container)
                                
                                # Verifica se já temos este documento (evita duplicatas)
                                is_duplicate = any(doc['title'] == title and doc['date_str'] == date_info['date_str'] 
                                                 for doc in valid_documents)
                                
                                if not is_duplicate:
                                    valid_documents.append({
                                        'container': container,
                                        'download_icon': download_icon,
                                        'date': date_info['date'],
                                        'date_str': date_info['date_str'],
                                        'title': title
                                    })
                                    print(f"   🎯 Documento válido adicionado!")
                                    print(f"      📄 {title[:60]}...")
                                else:
                                    print(f"   ⏭️ Documento duplicado, ignorado")
                            else:
                                print(f"   ❌ Ícone de download não encontrado")
                        else:
                            print(f"   ❌ Container não encontrado")
                    else:
                        print(f"   ⏭️ Data {date_info['date_str']} fora do período")
                else:
                    print(f"   ❌ Data não identificada no contexto")
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar elemento: {e}")
                continue
                
        print(f"\n📋 Documentos únicos encontrados: {len(valid_documents)}")
        
        if valid_documents:
            print("📄 Lista de downloads:")
            for i, doc in enumerate(valid_documents):
                print(f"   {i+1}. {doc['title'][:60]}... ({doc['date_str']})")
                
        return valid_documents
        
    def extract_date_from_context(self, element):
        """Extrai data analisando o contexto ao redor do elemento"""
        try:
            # Estratégia: sobe na hierarquia coletando texto até formar uma data completa
            current = element
            combined_text = ""
            
            for level in range(20):
                try:
                    parent = current.find_element(By.XPATH, "./..")
                    parent_text = parent.text.strip()
                    
                    # Se o texto do pai contém uma data completa, usa ele
                    date_match = self.extract_date_from_text(parent_text)
                    if date_match:
                        return date_match
                        
                    current = parent
                    
                except:
                    break
                    
            # Se não encontrou data completa, tenta o texto do próprio elemento
            elem_text = element.text.strip()
            date_match = self.extract_date_from_text(elem_text)
            if date_match:
                return date_match
                
            return None
            
        except:
            return None
            
    def extract_date_from_text(self, text):
        """Extrai data de um texto usando regex"""
        try:
            # Padrões de data
            patterns = [
                r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})',
                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})'
            ]
            
            month_map = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    groups = match.groups()
                    
                    try:
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
                            date_obj = datetime(year, month, day)
                            
                            return {
                                'date': date_obj,
                                'date_str': date_obj.strftime('%d %b %Y'),
                                'matched_text': match.group()
                            }
                            
                    except (ValueError, KeyError):
                        continue
                        
            return None
            
        except:
            return None
            
    def find_document_container_smart(self, element):
        """Encontra container do documento usando busca inteligente"""
        current = element
        
        # Sobe na hierarquia procurando por um container que pareça um documento completo
        for level in range(25):
            try:
                parent = current.find_element(By.XPATH, "./..")
                
                if self.is_document_container_smart(parent):
                    return parent
                    
                current = parent
                
            except:
                break
                
        return None
        
    def is_document_container_smart(self, element):
        """Verifica se elemento é um container de documento usando critérios inteligentes"""
        try:
            text = element.text.strip()
            
            # Critérios para ser um container de documento
            has_substantial_content = len(text) > 150
            has_multiple_lines = len(text.split('\n')) >= 6
            
            # Palavras-chave que indicam um documento
            doc_keywords = [
                'GLB', 'LAC', 'Bulletin', 'announcement', 'Mastercard',
                'Publication Date', 'Effective Date', 'Audience', 'Type', 'Region'
            ]
            
            has_doc_keywords = sum(1 for keyword in doc_keywords if keyword in text) >= 2
            
            # Deve ser um elemento container
            tag = element.tag_name.lower()
            is_container_tag = tag in ['div', 'article', 'section', 'li', 'td', 'tr']
            
            # Não deve ser muito grande (indicaria container pai demais)
            not_too_large = len(text) < 2000
            
            return (has_substantial_content and has_multiple_lines 
                   and has_doc_keywords and is_container_tag and not_too_large)
                   
        except:
            return False
            
    def find_download_icon_in_container_smart(self, container):
        """Busca inteligente por ícones de download"""
        print(f"   🔍 Procurando ícone de download no container...")
        
        # Múltiplas estratégias de busca
        all_candidates = []
        
        # 1. Busca por elementos obviamente clicáveis
        clickable_selectors = [
            './/a', './/button', './/*[@onclick]', './/*[@role="button"]'
        ]
        
        for selector in clickable_selectors:
            try:
                elements = container.find_elements(By.XPATH, selector)
                all_candidates.extend(elements)
            except:
                continue
                
        # 2. Busca por ícones e SVGs
        icon_selectors = [
            './/i', './/svg', './/*[contains(@class, "icon")]'
        ]
        
        for selector in icon_selectors:
            try:
                elements = container.find_elements(By.XPATH, selector)
                all_candidates.extend(elements)
            except:
                continue
                
        # Remove duplicatas e elementos invisíveis
        unique_candidates = []
        for candidate in all_candidates:
            if candidate not in unique_candidates:
                try:
                    # Verifica se é visível e tem tamanho razoável
                    rect = candidate.rect
                    if rect and rect['width'] > 0 and rect['height'] > 0:
                        unique_candidates.append(candidate)
                except:
                    unique_candidates.append(candidate)
                    
        print(f"      📊 Candidatos únicos: {len(unique_candidates)}")
        
        # Avalia cada candidato
        best_candidate = None
        best_score = 0
        
        for i, candidate in enumerate(unique_candidates):
            score = self.evaluate_download_candidate_smart(candidate, container)
            
            if score > 0:
                print(f"         {i+1}. <{candidate.tag_name}> score: {score}")
                
                if score > best_score:
                    best_score = score
                    best_candidate = candidate
                    
        if best_candidate and best_score >= 2:
            print(f"      ✅ Melhor candidato: <{best_candidate.tag_name}> (score: {best_score})")
            return best_candidate
        else:
            print(f"      ❌ Nenhum candidato válido (melhor score: {best_score})")
            return None
            
    def evaluate_download_candidate_smart(self, element, container):
        """Avalia candidato a ícone de download com critérios inteligentes"""
        score = 0
        
        try:
            # Atributos
            tag = element.tag_name.lower()
            classes = element.get_attribute('class') or ''
            href = element.get_attribute('href') or ''
            onclick = element.get_attribute('onclick') or ''
            title = element.get_attribute('title') or ''
            innerHTML = element.get_attribute('innerHTML') or ''
            
            all_text = f"{classes} {href} {onclick} {title} {innerHTML}".lower()
            
            # 1. Palavras-chave fortes (+4 pontos)
            strong_keywords = ['download', 'zip', 'pdf']
            for keyword in strong_keywords:
                if keyword in all_text:
                    score += 4
                    
            # 2. Palavras-chave moderadas (+2 pontos)
            moderate_keywords = ['file', 'export', 'save', 'arrow-down']
            for keyword in moderate_keywords:
                if keyword in all_text:
                    score += 2
                    
            # 3. Elementos clicáveis (+2 pontos)
            if tag in ['a', 'button'] or onclick or href:
                score += 2
                
            # 4. Ícones (+1 ponto)
            if tag in ['i', 'svg'] or 'icon' in classes:
                score += 1
                
            # 5. Posição no lado direito (+2 pontos)
            try:
                elem_rect = element.rect
                container_rect = container.rect
                
                if elem_rect and container_rect:
                    # Lado direito do container
                    container_right_third = container_rect['x'] + (container_rect['width'] * 0.67)
                    if elem_rect['x'] >= container_right_third:
                        score += 2
                        
            except:
                pass
                
            # 6. Tamanho adequado para ícone (+1 ponto)
            try:
                rect = element.rect
                if rect:
                    width, height = rect['width'], rect['height']
                    if 10 <= width <= 80 and 10 <= height <= 80:
                        score += 1
                        
            except:
                pass
                
            # 7. Penaliza elementos com muito texto (-2 pontos)
            text = element.text.strip()
            if len(text) > 50:
                score -= 2
                
        except:
            pass
            
        return max(0, score)  # Score mínimo 0
        
    def get_document_title_smart(self, container):
        """Extrai título do documento de forma inteligente"""
        try:
            lines = container.text.strip().split('\n')
            
            # Procura por linha que parece título (com códigos como GLB, LAC)
            for line in lines:
                line = line.strip()
                
                # Pula metadados
                if any(skip in line for skip in ['Audience:', 'Type:', 'Region:', 'Category:', 'Publication Date:', 'Effective Date:']):
                    continue
                    
                # Códigos de documento
                if re.match(r'^[A-Z]{2,4}\s+\d+', line):
                    return line
                    
                # Linha substancial que pode ser título
                if len(line) > 30 and not line.lower().startswith('mastercom'):
                    return line
                    
            # Se não encontrou, usa primeira linha não-metadado
            for line in lines:
                line = line.strip()
                if len(line) > 15 and ':' not in line:
                    return line
                    
            return "Documento sem título"
            
        except:
            return "Documento sem título"
            
    def download_documents(self, documents):
        """Executa downloads dos documentos"""
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
                
                # Scroll e destaque
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", doc['container'])
                time.sleep(2)
                
                self.driver.execute_script("arguments[0].style.border='3px solid red'; arguments[0].style.backgroundColor='yellow';", doc['download_icon'])
                time.sleep(1)
                
                print("   🖱️ Clicando no ícone...")
                
                # Múltiplas tentativas de clique
                click_methods = [
                    lambda: doc['download_icon'].click(),
                    lambda: self.driver.execute_script("arguments[0].click();", doc['download_icon']),
                    lambda: actions.move_to_element(doc['download_icon']).click().perform()
                ]
                
                clicked = False
                for j, method in enumerate(click_methods):
                    try:
                        method()
                        print(f"      ✅ Método {j+1} funcionou")
                        clicked = True
                        break
                    except Exception as e:
                        print(f"      ⚠️ Método {j+1} falhou: {e}")
                        
                # Remove destaque
                self.driver.execute_script("arguments[0].style.border=''; arguments[0].style.backgroundColor='';", doc['download_icon'])
                
                if clicked:
                    print("   ⏳ Aguardando download...")
                    
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
                        print(f"   ⚠️ Download não detectado")
                        
                time.sleep(4)
                
            except Exception as e:
                print(f"   ❌ Erro no download: {e}")
                continue
                
        return downloaded_files
        
    def wait_for_download(self, timeout=45):
        """Aguarda download"""
        start_time = time.time()
        initial_files = set(f.name for f in self.download_dir.glob("*") if f.is_file())
        
        while time.time() - start_time < timeout:
            current_files = set(f.name for f in self.download_dir.glob("*") if f.is_file())
            new_files = current_files - initial_files
            
            complete_files = []
            for filename in new_files:
                if not filename.endswith(('.crdownload', '.tmp', '.part')):
                    file_path = self.download_dir / filename
                    if file_path.exists() and file_path.stat().st_size > 500:
                        complete_files.append(filename)
                        
            if complete_files:
                return self.download_dir / complete_files[0]
                
            time.sleep(3)
            
        return None
        
    def extract_pdfs(self, downloaded_files):
        """Extrai PDFs"""
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
        """Executa o downloader"""
        print("🧠 MASTERCARD SMART DOWNLOADER")
        print("=" * 60)
        
        try:
            self.setup_chrome()
            self.navigate_to_announcements()
            
            documents = self.find_document_containers_smart()
            
            if not documents:
                print("❌ Nenhum documento encontrado")
                return False
                
            downloaded_files = self.download_documents(documents)
            extracted_pdfs = self.extract_pdfs(downloaded_files)
            
            # Verifica arquivos na pasta
            all_files = list(self.download_dir.glob("*"))
            
            range_start, range_end = self.get_target_date_range()
            
            print("\n" + "="*60)
            print("🎉 PROCESSO CONCLUÍDO!")
            print(f"📅 Período: {range_start.strftime('%d %b')} - {range_end.strftime('%d %b %Y')}")
            print(f"📋 Documentos encontrados: {len(documents)}")
            print(f"📥 Downloads detectados: {len(downloaded_files)}")
            print(f"📄 PDFs extraídos: {len(extracted_pdfs)}")
            print(f"📁 Arquivos totais: {len(all_files)}")
            
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
    downloader = SmartDownloader()
    
    try:
        success = downloader.run()
        
        if success:
            print("\n🎉 SUCESSO!")
        else:
            print("\n😔 Nenhum arquivo encontrado")
            
    except KeyboardInterrupt:
        print("\n⏹️ Interrompido")

if __name__ == "__main__":
    main()
