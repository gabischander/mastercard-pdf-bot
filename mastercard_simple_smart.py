#!/usr/bin/env python3
"""
Mastercard Simple Smart Downloader
Versão simplificada que aceita qualquer container com elementos clicáveis
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

class SimpleSmartDownloader:
    def __init__(self):
        self.download_dir = Path("downloads_simple_smart")
        self.pdf_dir = Path("pdfs_simple_smart")
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
        
    def find_document_containers_simple(self):
        """Encontra containers de forma simples"""
        print(f"\n🔍 Busca simples por documentos com datas...")
        
        range_start, range_end = self.get_target_date_range()
        
        # Procura por elementos que contêm "Jul" ou "Jun"
        month_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Jul') or contains(text(), 'Jun')]")
        print(f"📋 Elementos com Jul/Jun: {len(month_elements)}")
        
        valid_documents = []
        
        for i, month_elem in enumerate(month_elements):
            try:
                print(f"\n📅 Elemento {i+1}/{len(month_elements)}:")
                
                # Extrai data do contexto
                date_info = self.extract_date_simple(month_elem)
                
                if date_info and range_start <= date_info['date'] <= range_end:
                    print(f"   📅 Data válida: {date_info['date_str']}")
                    
                    # Procura container mais simples
                    containers = self.find_containers_simple(month_elem)
                    
                    for container in containers:
                        # Procura elementos clicáveis no container
                        clickables = self.find_clickables_in_container(container)
                        
                        if clickables:
                            print(f"   📦 Container com {len(clickables)} elementos clicáveis")
                            
                            # Pega o melhor candidato a download
                            best_clickable = self.get_best_download_candidate(clickables, container)
                            
                            if best_clickable:
                                title = self.get_title_simple(container)
                                
                                # Evita duplicatas
                                is_duplicate = any(doc['title'] == title and doc['date_str'] == date_info['date_str'] 
                                                 for doc in valid_documents)
                                
                                if not is_duplicate:
                                    valid_documents.append({
                                        'container': container,
                                        'download_icon': best_clickable,
                                        'date': date_info['date'],
                                        'date_str': date_info['date_str'],
                                        'title': title
                                    })
                                    print(f"   ✅ Documento adicionado: {title[:40]}...")
                                    break
                                else:
                                    print(f"   ⏭️ Documento duplicado")
                                    
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                continue
                
        print(f"\n📋 Documentos encontrados: {len(valid_documents)}")
        
        if valid_documents:
            print("📄 Lista:")
            for i, doc in enumerate(valid_documents):
                print(f"   {i+1}. {doc['title'][:50]}... ({doc['date_str']})")
                
        return valid_documents
        
    def extract_date_simple(self, element):
        """Extrai data de forma simples"""
        try:
            # Tenta diferentes níveis da hierarquia
            for level in range(15):
                try:
                    if level == 0:
                        text = element.text.strip()
                    else:
                        parent = element
                        for _ in range(level):
                            parent = parent.find_element(By.XPATH, "./..")
                        text = parent.text.strip()
                        
                    # Procura padrões de data
                    pattern = r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})'
                    match = re.search(pattern, text, re.IGNORECASE)
                    
                    if match:
                        day, month_str, year = match.groups()
                        
                        month_map = {
                            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                        }
                        
                        if month_str in month_map:
                            date_obj = datetime(int(year), month_map[month_str], int(day))
                            return {
                                'date': date_obj,
                                'date_str': date_obj.strftime('%d %b %Y')
                            }
                            
                except:
                    continue
                    
            return None
            
        except:
            return None
            
    def find_containers_simple(self, element):
        """Encontra containers de forma simples"""
        containers = []
        current = element
        
        # Sobe na hierarquia coletando containers
        for level in range(12):
            try:
                if level > 0:
                    current = current.find_element(By.XPATH, "./..")
                    
                # Adiciona se parece ser um container
                if self.is_valid_container_simple(current):
                    containers.append(current)
                    
            except:
                break
                
        return containers
        
    def is_valid_container_simple(self, element):
        """Verifica se é um container válido (critérios simples)"""
        try:
            text = element.text.strip()
            tag = element.tag_name.lower()
            
            # Critérios bem simples
            has_content = len(text) > 50
            is_container = tag in ['div', 'section', 'article', 'li', 'td', 'tr']
            not_too_big = len(text) < 5000
            
            return has_content and is_container and not_too_big
            
        except:
            return False
            
    def find_clickables_in_container(self, container):
        """Encontra elementos clicáveis no container"""
        clickables = []
        
        # Diferentes tipos de elementos clicáveis
        selectors = [
            './/a', './/button', './/*[@onclick]', './/*[@role="button"]',
            './/i', './/svg', './/*[contains(@class, "icon")]',
            './/*[contains(@class, "btn")]', './/*[contains(@class, "click")]'
        ]
        
        for selector in selectors:
            try:
                elements = container.find_elements(By.XPATH, selector)
                for elem in elements:
                    if elem not in clickables:
                        # Verifica se é visível
                        try:
                            rect = elem.rect
                            if rect and rect['width'] > 0 and rect['height'] > 0:
                                clickables.append(elem)
                        except:
                            clickables.append(elem)
                            
            except:
                continue
                
        return clickables
        
    def get_best_download_candidate(self, clickables, container):
        """Encontra o melhor candidato a download"""
        scored_candidates = []
        
        for clickable in clickables:
            score = self.score_clickable_simple(clickable, container)
            if score > 0:
                scored_candidates.append((clickable, score))
                
        if scored_candidates:
            # Ordena por score decrescente
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            return scored_candidates[0][0]  # Retorna o melhor
            
        return None
        
    def score_clickable_simple(self, element, container):
        """Pontua elemento clicável de forma simples"""
        score = 0
        
        try:
            tag = element.tag_name.lower()
            classes = element.get_attribute('class') or ''
            href = element.get_attribute('href') or ''
            onclick = element.get_attribute('onclick') or ''
            title = element.get_attribute('title') or ''
            text = element.text.strip().lower()
            
            all_text = f"{classes} {href} {onclick} {title} {text}".lower()
            
            # Pontuação por palavras-chave
            if 'download' in all_text: score += 5
            if 'zip' in all_text: score += 4
            if 'pdf' in all_text: score += 4
            if 'file' in all_text: score += 2
            if 'export' in all_text: score += 2
            if 'arrow' in all_text: score += 2
            
            # Pontuação por tipo de elemento
            if tag in ['a', 'button']: score += 2
            if onclick: score += 2
            if href: score += 1
            if tag in ['i', 'svg']: score += 1
            
            # Bonificação por posição (lado direito)
            try:
                elem_rect = element.rect
                container_rect = container.rect
                
                if elem_rect and container_rect:
                    container_right_half = container_rect['x'] + (container_rect['width'] / 2)
                    if elem_rect['x'] >= container_right_half:
                        score += 2
                        
            except:
                pass
                
            # Penalização por muito texto
            if len(text) > 30:
                score -= 1
                
            # Bonificação por tamanho de ícone
            try:
                rect = element.rect
                if rect:
                    width, height = rect['width'], rect['height']
                    if 15 <= width <= 60 and 15 <= height <= 60:
                        score += 1
                        
            except:
                pass
                
        except:
            pass
            
        return score
        
    def get_title_simple(self, container):
        """Extrai título de forma simples"""
        try:
            text = container.text.strip()
            lines = text.split('\n')
            
            # Procura primeira linha que parece título
            for line in lines:
                line = line.strip()
                if len(line) > 20 and not ':' in line:
                    return line
                    
            # Se não encontrou, usa primeira linha não vazia
            for line in lines:
                line = line.strip()
                if len(line) > 10:
                    return line
                    
            return "Documento"
            
        except:
            return "Documento"
            
    def download_documents(self, documents):
        """Executa downloads"""
        if not documents:
            print("❌ Nenhum documento para baixar")
            return []
            
        print(f"\n📥 Iniciando downloads de {len(documents)} documentos...")
        
        downloaded_files = []
        actions = ActionChains(self.driver)
        
        for i, doc in enumerate(documents):
            try:
                print(f"\n📥 Download {i+1}/{len(documents)}:")
                print(f"   📄 {doc['title'][:50]}...")
                print(f"   📅 {doc['date_str']}")
                
                # Scroll e destaque
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", doc['container'])
                time.sleep(2)
                
                # Destaca o elemento clicável
                self.driver.execute_script("arguments[0].style.border='4px solid red'; arguments[0].style.backgroundColor='yellow';", doc['download_icon'])
                time.sleep(2)
                
                print("   🖱️ Clicando...")
                
                # Tenta clicar
                clicked = False
                try:
                    doc['download_icon'].click()
                    clicked = True
                    print("      ✅ Clique direto funcionou")
                except:
                    try:
                        self.driver.execute_script("arguments[0].click();", doc['download_icon'])
                        clicked = True
                        print("      ✅ Clique JavaScript funcionou")
                    except:
                        try:
                            actions.move_to_element(doc['download_icon']).click().perform()
                            clicked = True
                            print("      ✅ ActionChains funcionou")
                        except Exception as e:
                            print(f"      ❌ Todos os cliques falharam: {e}")
                
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
                        print(f"   ✅ Download: {downloaded_file.name}")
                    else:
                        print(f"   ⚠️ Download não detectado")
                        
                time.sleep(5)
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                continue
                
        return downloaded_files
        
    def wait_for_download(self, timeout=30):
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
                    if file_path.exists() and file_path.stat().st_size > 100:
                        complete_files.append(filename)
                        
            if complete_files:
                return self.download_dir / complete_files[0]
                
            time.sleep(2)
            
        return None
        
    def run(self):
        """Executa o downloader"""
        print("🚀 MASTERCARD SIMPLE SMART DOWNLOADER")
        print("=" * 60)
        
        try:
            self.setup_chrome()
            self.navigate_to_announcements()
            
            documents = self.find_document_containers_simple()
            
            if not documents:
                print("❌ Nenhum documento encontrado")
                return False
                
            downloaded_files = self.download_documents(documents)
            
            # Verifica arquivos baixados
            all_files = list(self.download_dir.glob("*"))
            
            range_start, range_end = self.get_target_date_range()
            
            print("\n" + "="*60)
            print("🎉 RESULTADO FINAL!")
            print(f"📅 Período: {range_start.strftime('%d %b')} - {range_end.strftime('%d %b %Y')}")
            print(f"📋 Documentos processados: {len(documents)}")
            print(f"📥 Downloads detectados: {len(downloaded_files)}")
            print(f"📁 Arquivos na pasta: {len(all_files)}")
            
            if all_files:
                print(f"\n📁 ARQUIVOS BAIXADOS:")
                for file in all_files:
                    print(f"  • {file.name} ({file.stat().st_size} bytes)")
                    
            return len(all_files) > 0
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
            
        finally:
            if self.driver:
                input("\nPressione ENTER para fechar o navegador...")
                self.driver.quit()

def main():
    downloader = SimpleSmartDownloader()
    
    try:
        success = downloader.run()
        
        if success:
            print("\n🎉 DOWNLOADS CONCLUÍDOS!")
        else:
            print("\n😔 Nenhum download realizado")
            
    except KeyboardInterrupt:
        print("\n⏹️ Interrompido")

if __name__ == "__main__":
    main()
