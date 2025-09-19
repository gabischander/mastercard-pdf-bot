#!/usr/bin/env python3
"""
Mastercard Fresh Elements Downloader
Re-localiza elementos no momento do clique para evitar stale reference
"""

import time
import re
from datetime import datetime, timedelta
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

class FreshElementsDownloader:
    def __init__(self):
        self.download_dir = Path("downloads_fresh")
        self.pdf_dir = Path("pdfs_fresh")
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
        """Calcula período"""
        today = datetime.now()
        
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
        
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            print("✅ Usando última aba")
            
        time.sleep(8)
        
    def find_clickables_with_selectors(self):
        """Encontra elementos clicáveis e guarda seus seletores para re-localização"""
        print(f"\n🔍 Mapeando elementos clicáveis com seletores...")
        
        range_start, range_end = self.get_target_date_range()
        
        # Encontra todos os elementos clicáveis e guarda informações para re-localização
        clickable_selectors = []
        
        # Diferentes tipos de seletores
        base_selectors = [
            '//a', '//button', '//*[@onclick]', '//*[@role="button"]',
            '//i', '//svg', '//*[contains(@class, "icon")]'
        ]
        
        for selector in base_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                
                for elem in elements:
                    try:
                        # Cria seletor único para este elemento
                        unique_selector = self.create_unique_selector(elem)
                        
                        if unique_selector:
                            # Verifica se está próximo a uma data válida
                            date_info = self.find_nearby_date(elem, range_start, range_end)
                            
                            if date_info:
                                score = self.score_element(elem)
                                
                                if score > 0:
                                    clickable_selectors.append({
                                        'selector': unique_selector,
                                        'date': date_info['date'],
                                        'date_str': date_info['date_str'],
                                        'score': score,
                                        'context': self.get_context(elem)
                                    })
                                    
                    except:
                        continue
                        
            except:
                continue
                
        print(f"📋 Elementos com seletores únicos: {len(clickable_selectors)}")
        
        if clickable_selectors:
            # Ordena por score
            clickable_selectors.sort(key=lambda x: x['score'], reverse=True)
            
            print("🎯 Top candidatos:")
            for i, item in enumerate(clickable_selectors[:10]):
                print(f"   {i+1}. Score: {item['score']} | Data: {item['date_str']} | {item['context'][:40]}...")
                
            # Remove duplicatas por contexto
            unique_selectors = []
            seen_contexts = set()
            
            for item in clickable_selectors:
                context_key = item['context'][:50].lower().strip()
                if context_key not in seen_contexts and context_key != "sem contexto":
                    unique_selectors.append(item)
                    seen_contexts.add(context_key)
                    
            print(f"📋 Seletores únicos após filtro: {len(unique_selectors)}")
            
            return unique_selectors[:8]  # Máximo 8
            
        return []
        
    def create_unique_selector(self, element):
        """Cria seletor único para re-localizar elemento"""
        try:
            # Estratégia 1: ID único
            elem_id = element.get_attribute('id')
            if elem_id:
                return f'//*[@id="{elem_id}"]'
                
            # Estratégia 2: Combinação de tag + classes + texto
            tag = element.tag_name.lower()
            classes = element.get_attribute('class') or ''
            text = element.text.strip()
            
            if classes:
                class_selector = f'[contains(@class, "{classes.split()[0]}")]'
            else:
                class_selector = ''
                
            if text and len(text) < 30:
                text_selector = f'[contains(text(), "{text[:20]}")]'
            else:
                text_selector = ''
                
            # Estratégia 3: Posição na hierarquia
            try:
                parent = element.find_element(By.XPATH, "./..")
                parent_tag = parent.tag_name.lower()
                siblings = parent.find_elements(By.TAG_NAME, tag)
                
                if len(siblings) > 1:
                    index = siblings.index(element) + 1
                    position_selector = f'[{index}]'
                else:
                    position_selector = ''
                    
            except:
                position_selector = ''
                
            # Constrói seletor
            selector = f'//{tag}{class_selector}{text_selector}{position_selector}'
            
            # Testa se o seletor é único
            try:
                test_elements = self.driver.find_elements(By.XPATH, selector)
                if len(test_elements) == 1:
                    return selector
                    
            except:
                pass
                
            # Fallback: seletor mais simples
            if classes:
                return f'//{tag}[contains(@class, "{classes.split()[0]}")]'
            else:
                return f'//{tag}'
                
        except:
            return None
            
    def find_nearby_date(self, element, range_start, range_end):
        """Procura por datas próximas ao elemento"""
        try:
            current = element
            
            for level in range(12):
                try:
                    if level > 0:
                        current = current.find_element(By.XPATH, "./..")
                    
                    text = current.text.strip()
                    
                    # Procura padrões de data
                    pattern = r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})'
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    
                    for match in matches:
                        day, month_str, year = match.groups()
                        
                        month_map = {
                            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                        }
                        
                        if month_str in month_map:
                            try:
                                date_obj = datetime(int(year), month_map[month_str], int(day))
                                
                                if range_start <= date_obj <= range_end:
                                    return {
                                        'date': date_obj,
                                        'date_str': date_obj.strftime('%d %b %Y')
                                    }
                                    
                            except ValueError:
                                continue
                                
                except:
                    break
                    
            return None
            
        except:
            return None
            
    def score_element(self, element):
        """Pontua elemento"""
        score = 0
        
        try:
            tag = element.tag_name.lower()
            classes = element.get_attribute('class') or ''
            href = element.get_attribute('href') or ''
            onclick = element.get_attribute('onclick') or ''
            title = element.get_attribute('title') or ''
            text = element.text.strip().lower()
            
            all_text = f"{classes} {href} {onclick} {title} {text}".lower()
            
            # Pontuação alta
            if 'download' in all_text: score += 15
            if 'zip' in all_text: score += 12
            if 'pdf' in all_text: score += 12
            if 'file' in all_text: score += 8
            if 'export' in all_text: score += 8
            
            # Pontuação moderada
            if 'arrow' in all_text: score += 5
            if 'save' in all_text: score += 5
            
            # Tipo de elemento
            if tag == 'a' and href: score += 6
            if tag == 'button': score += 5
            if onclick: score += 5
            if tag in ['i', 'svg']: score += 4
            
            # Classes específicas
            if 'btn' in classes: score += 3
            if 'icon' in classes: score += 3
            
            # Penalizações
            if len(text) > 30: score -= 5
            if len(text) > 50: score -= 8
            
            # Bonificação por tamanho (ícones têm tamanho específico)
            try:
                rect = element.rect
                if rect:
                    width, height = rect['width'], rect['height']
                    if 15 <= width <= 60 and 15 <= height <= 60:
                        score += 4
                    elif width < 5 or height < 5:
                        score -= 8
                        
            except:
                pass
                
        except:
            pass
            
        return max(0, score)
        
    def get_context(self, element):
        """Pega contexto do elemento"""
        try:
            for level in range(3):
                try:
                    if level == 0:
                        current = element
                    else:
                        current = element
                        for _ in range(level):
                            current = current.find_element(By.XPATH, "./..")
                            
                    text = current.text.strip()
                    if len(text) > 20:
                        return text[:80]
                        
                except:
                    continue
                    
            return element.text.strip()[:50] or "Sem contexto"
            
        except:
            return "Sem contexto"
            
    def download_by_selectors(self, selector_items):
        """Faz downloads re-localizando elementos pelos seletores"""
        if not selector_items:
            print("❌ Nenhum seletor para download")
            return []
            
        print(f"\n📥 Tentando downloads com {len(selector_items)} seletores...")
        
        downloaded_files = []
        actions = ActionChains(self.driver)
        
        for i, item in enumerate(selector_items):
            try:
                print(f"\n📥 Download {i+1}/{len(selector_items)}:")
                print(f"   📊 Score: {item['score']}")
                print(f"   📅 Data: {item['date_str']}")
                print(f"   📄 Contexto: {item['context'][:50]}...")
                print(f"   🔍 Seletor: {item['selector'][:60]}...")
                
                # Re-localiza elemento usando o seletor
                try:
                    elements = self.driver.find_elements(By.XPATH, item['selector'])
                    
                    if not elements:
                        print("      ❌ Elemento não encontrado com seletor")
                        continue
                        
                    element = elements[0]  # Pega o primeiro
                    
                    # Verifica se o elemento é válido
                    if not element.is_displayed() or not element.is_enabled():
                        print("      ❌ Elemento não visível/habilitado")
                        continue
                        
                except Exception as e:
                    print(f"      ❌ Erro ao localizar elemento: {e}")
                    continue
                
                # Scroll para o elemento
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(2)
                except:
                    pass
                
                # Destaca elemento
                try:
                    self.driver.execute_script(
                        "arguments[0].style.border='4px solid red'; arguments[0].style.backgroundColor='yellow'; arguments[0].style.zIndex='9999';", 
                        element
                    )
                    time.sleep(2)
                except:
                    pass
                
                print("      🖱️ Clicando...")
                
                # Tenta clicar
                clicked = False
                click_methods = [
                    ("Clique direto", lambda: element.click()),
                    ("JavaScript click", lambda: self.driver.execute_script("arguments[0].click();", element)),
                    ("ActionChains", lambda: actions.move_to_element(element).click().perform())
                ]
                
                for method_name, method in click_methods:
                    try:
                        method()
                        clicked = True
                        print(f"         ✅ {method_name} funcionou")
                        break
                    except Exception as e:
                        print(f"         ❌ {method_name} falhou: {e}")
                        
                # Remove destaque
                try:
                    self.driver.execute_script(
                        "arguments[0].style.border=''; arguments[0].style.backgroundColor=''; arguments[0].style.zIndex='';", 
                        element
                    )
                except:
                    pass
                
                if clicked:
                    print("      ⏳ Aguardando possível download...")
                    
                    # Aguarda e verifica download
                    time.sleep(6)
                    
                    downloaded_file = self.check_for_download()
                    
                    if downloaded_file:
                        downloaded_files.append({
                            'file': downloaded_file,
                            'date_str': item['date_str'],
                            'score': item['score'],
                            'context': item['context']
                        })
                        print(f"      ✅ Download detectado: {downloaded_file.name}")
                    else:
                        print("      ⚠️ Nenhum download detectado")
                        
                time.sleep(3)  # Pausa entre tentativas
                
            except Exception as e:
                print(f"      ❌ Erro geral: {e}")
                continue
                
        return downloaded_files
        
    def check_for_download(self):
        """Verifica se houve download recente"""
        try:
            files = list(self.download_dir.glob("*"))
            
            for file in files:
                if file.is_file():
                    file_time = file.stat().st_mtime
                    current_time = time.time()
                    
                    # Arquivo dos últimos 15 segundos
                    if current_time - file_time < 15:
                        return file
                        
            return None
            
        except:
            return None
            
    def run(self):
        """Executa o downloader"""
        print("🔄 MASTERCARD FRESH ELEMENTS DOWNLOADER")
        print("=" * 60)
        
        try:
            self.setup_chrome()
            self.navigate_to_announcements()
            
            selector_items = self.find_clickables_with_selectors()
            
            if not selector_items:
                print("❌ Nenhum elemento candidato encontrado")
                return False
                
            downloaded_files = self.download_by_selectors(selector_items)
            
            # Verifica todos os arquivos
            all_files = list(self.download_dir.glob("*"))
            
            range_start, range_end = self.get_target_date_range()
            
            print("\n" + "="*60)
            print("🎉 RESULTADO FINAL!")
            print(f"📅 Período: {range_start.strftime('%d %b')} - {range_end.strftime('%d %b %Y')}")
            print(f"🎯 Tentativas realizadas: {len(selector_items)}")
            print(f"📥 Downloads detectados: {len(downloaded_files)}")
            print(f"📁 Arquivos na pasta: {len(all_files)}")
            
            if all_files:
                print(f"\n📁 ARQUIVOS BAIXADOS:")
                for file in all_files:
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"  • {file.name} ({size_mb:.2f} MB)")
                    
            return len(all_files) > 0
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
            
        finally:
            if self.driver:
                input("\nPressione ENTER para fechar o navegador...")
                self.driver.quit()

def main():
    downloader = FreshElementsDownloader()
    
    try:
        success = downloader.run()
        
        if success:
            print("\n🎉 DOWNLOADS REALIZADOS COM SUCESSO!")
        else:
            print("\n😔 Nenhum download foi realizado")
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo interrompido")

if __name__ == "__main__":
    main()
