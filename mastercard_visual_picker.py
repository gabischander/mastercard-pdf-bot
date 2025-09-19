#!/usr/bin/env python3
"""
Mastercard Visual Picker
Mostra todos os elementos clicáveis na tela para o usuário escolher
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

class VisualPickerDownloader:
    def __init__(self):
        self.download_dir = Path("downloads_visual")
        self.pdf_dir = Path("pdfs_visual")
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
        
    def highlight_and_show_clickables(self):
        """Destaca todos os elementos clicáveis e mostra para escolha"""
        print(f"\n🎨 Destacando elementos clicáveis na página...")
        
        range_start, range_end = self.get_target_date_range()
        
        # Encontra elementos próximos a datas válidas
        clickable_candidates = []
        
        # Diferentes tipos de elementos clicáveis
        selectors = [
            '//a', '//button', '//*[@onclick]', '//*[@role="button"]',
            '//i', '//svg', '//*[contains(@class, "icon")]',
            '//*[contains(@class, "btn")]'
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                
                for elem in elements:
                    try:
                        # Verifica se está próximo a uma data válida
                        date_info = self.find_nearby_date(elem, range_start, range_end)
                        
                        if date_info:
                            # Calcula score
                            score = self.score_element(elem)
                            
                            if score > 0:
                                clickable_candidates.append({
                                    'element': elem,
                                    'date': date_info['date'],
                                    'date_str': date_info['date_str'],
                                    'score': score,
                                    'context': self.get_context(elem),
                                    'position': self.get_position_info(elem)
                                })
                                
                    except:
                        continue
                        
            except:
                continue
                
        # Remove duplicatas
        unique_candidates = []
        seen_positions = set()
        
        for candidate in clickable_candidates:
            pos_key = f"{candidate['position']['x']},{candidate['position']['y']}"
            if pos_key not in seen_positions:
                unique_candidates.append(candidate)
                seen_positions.add(pos_key)
                
        # Ordena por score
        unique_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"📋 Elementos únicos encontrados: {len(unique_candidates)}")
        
        if not unique_candidates:
            print("❌ Nenhum elemento candidato encontrado")
            return []
            
        # Destaca elementos na página
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow']
        
        highlighted_elements = []
        
        for i, candidate in enumerate(unique_candidates[:8]):  # Máximo 8
            try:
                color = colors[i % len(colors)]
                
                # Destaca elemento na página
                self.driver.execute_script(f"""
                    arguments[0].style.border = '4px solid {color}';
                    arguments[0].style.backgroundColor = '{color}';
                    arguments[0].style.opacity = '0.8';
                    arguments[0].style.zIndex = '9999';
                    
                    // Adiciona número
                    var numberDiv = document.createElement('div');
                    numberDiv.innerHTML = '{i+1}';
                    numberDiv.style.position = 'absolute';
                    numberDiv.style.backgroundColor = '{color}';
                    numberDiv.style.color = 'white';
                    numberDiv.style.fontSize = '16px';
                    numberDiv.style.fontWeight = 'bold';
                    numberDiv.style.padding = '2px 6px';
                    numberDiv.style.borderRadius = '50%';
                    numberDiv.style.zIndex = '10000';
                    numberDiv.style.top = (arguments[0].getBoundingClientRect().top + window.scrollY - 20) + 'px';
                    numberDiv.style.left = (arguments[0].getBoundingClientRect().left + window.scrollX - 20) + 'px';
                    numberDiv.setAttribute('data-highlight-number', '{i+1}');
                    document.body.appendChild(numberDiv);
                """, candidate['element'])
                
                highlighted_elements.append(candidate)
                
            except:
                continue
                
        # Mostra lista para o usuário escolher
        print(f"\n🎯 ELEMENTOS DESTACADOS NA PÁGINA:")
        print("="*60)
        
        for i, candidate in enumerate(highlighted_elements):
            print(f"{i+1}. Score: {candidate['score']} | Data: {candidate['date_str']}")
            print(f"   📄 Contexto: {candidate['context'][:60]}...")
            print(f"   📍 Posição: x={candidate['position']['x']}, y={candidate['position']['y']}")
            print(f"   📏 Tamanho: {candidate['position']['width']}x{candidate['position']['height']}")
            print()
            
        print("="*60)
        print("👀 Olhe na página do navegador e veja os elementos destacados com números!")
        print("🎯 Escolha qual(is) elemento(s) são os ícones de download que você quer clicar.")
        print("💡 Dica: Os ícones de download geralmente são pequenos e estão no lado direito.")
        print()
        
        # Pergunta ao usuário
        while True:
            try:
                choice = input("Digite os números dos elementos para clicar (ex: 1,3,5) ou 'todos' para todos ou 'sair': ").strip().lower()
                
                if choice == 'sair':
                    return []
                elif choice == 'todos':
                    return highlighted_elements
                else:
                    # Parse da escolha
                    numbers = [int(n.strip()) for n in choice.split(',') if n.strip().isdigit()]
                    
                    if numbers:
                        selected = []
                        for num in numbers:
                            if 1 <= num <= len(highlighted_elements):
                                selected.append(highlighted_elements[num-1])
                                
                        if selected:
                            return selected
                        else:
                            print("❌ Números inválidos. Tente novamente.")
                    else:
                        print("❌ Formato inválido. Use números separados por vírgula (ex: 1,3,5)")
                        
            except ValueError:
                print("❌ Formato inválido. Use números separados por vírgula (ex: 1,3,5)")
                
    def find_nearby_date(self, element, range_start, range_end):
        """Procura por datas próximas ao elemento"""
        try:
            current = element
            
            for level in range(10):
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
        """Pontua elemento como candidato a download"""
        score = 0
        
        try:
            tag = element.tag_name.lower()
            classes = element.get_attribute('class') or ''
            href = element.get_attribute('href') or ''
            onclick = element.get_attribute('onclick') or ''
            title = element.get_attribute('title') or ''
            text = element.text.strip().lower()
            
            all_text = f"{classes} {href} {onclick} {title} {text}".lower()
            
            # Palavras-chave de download
            if 'download' in all_text: score += 20
            if 'zip' in all_text: score += 15
            if 'pdf' in all_text: score += 15
            if 'file' in all_text: score += 10
            if 'export' in all_text: score += 10
            if 'arrow' in all_text: score += 8
            if 'save' in all_text: score += 8
            
            # Tipo de elemento
            if tag == 'a' and href: score += 5
            if tag == 'button': score += 6
            if onclick: score += 6
            if tag in ['i', 'svg']: score += 8  # Ícones têm pontuação alta
            
            # Classes específicas
            if 'btn' in classes: score += 4
            if 'icon' in classes: score += 8
            if 'click' in classes: score += 4
            
            # Bonificação por tamanho de ícone (pequeno)
            try:
                rect = element.rect
                if rect:
                    width, height = rect['width'], rect['height']
                    if 10 <= width <= 50 and 10 <= height <= 50:
                        score += 10  # Tamanho ideal para ícone
                    elif width > 100 or height > 100:
                        score -= 5   # Muito grande
                        
            except:
                pass
                
            # Penalização por muito texto
            if len(text) > 20: score -= 5
            if len(text) > 50: score -= 10
            
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
                        return text[:100]
                        
                except:
                    continue
                    
            return element.text.strip()[:50] or "Sem contexto"
            
        except:
            return "Sem contexto"
            
    def get_position_info(self, element):
        """Pega informações de posição do elemento"""
        try:
            rect = element.rect
            return {
                'x': int(rect['x']),
                'y': int(rect['y']),
                'width': int(rect['width']),
                'height': int(rect['height'])
            }
        except:
            return {'x': 0, 'y': 0, 'width': 0, 'height': 0}
            
    def download_selected_elements(self, selected_elements):
        """Faz download dos elementos selecionados"""
        if not selected_elements:
            print("❌ Nenhum elemento selecionado")
            return []
            
        print(f"\n📥 Fazendo download de {len(selected_elements)} elementos...")
        
        downloaded_files = []
        actions = ActionChains(self.driver)
        
        for i, item in enumerate(selected_elements):
            try:
                print(f"\n📥 Download {i+1}/{len(selected_elements)}:")
                print(f"   📊 Score: {item['score']}")
                print(f"   📅 Data: {item['date_str']}")
                print(f"   📄 Contexto: {item['context'][:50]}...")
                
                element = item['element']
                
                # Scroll para o elemento
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(2)
                
                # Re-destaca o elemento
                self.driver.execute_script(
                    "arguments[0].style.border='6px solid lime'; arguments[0].style.backgroundColor='lime';", 
                    element
                )
                time.sleep(1)
                
                print("   🖱️ Clicando...")
                
                # Tenta clicar
                clicked = False
                try:
                    element.click()
                    clicked = True
                    print("      ✅ Clique direto")
                except:
                    try:
                        self.driver.execute_script("arguments[0].click();", element)
                        clicked = True
                        print("      ✅ Clique JavaScript")
                    except:
                        try:
                            actions.move_to_element(element).click().perform()
                            clicked = True
                            print("      ✅ ActionChains")
                        except Exception as e:
                            print(f"      ❌ Falha: {e}")
                
                if clicked:
                    print("   ⏳ Aguardando download...")
                    
                    time.sleep(8)  # Aguarda mais tempo
                    
                    downloaded_file = self.check_for_download()
                    
                    if downloaded_file:
                        downloaded_files.append({
                            'file': downloaded_file,
                            'date_str': item['date_str'],
                            'score': item['score'],
                            'context': item['context']
                        })
                        print(f"   ✅ Download: {downloaded_file.name}")
                    else:
                        print("   ⚠️ Nenhum download detectado")
                        
                time.sleep(3)
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                continue
                
        return downloaded_files
        
    def check_for_download(self):
        """Verifica se houve download"""
        try:
            files = list(self.download_dir.glob("*"))
            
            for file in files:
                if file.is_file():
                    file_time = file.stat().st_mtime
                    current_time = time.time()
                    
                    if current_time - file_time < 20:  # Últimos 20 segundos
                        return file
                        
            return None
            
        except:
            return None
            
    def cleanup_highlights(self):
        """Remove destaques da página"""
        try:
            self.driver.execute_script("""
                // Remove destaques dos elementos
                var highlightedElements = document.querySelectorAll('[style*="border"]');
                highlightedElements.forEach(function(elem) {
                    elem.style.border = '';
                    elem.style.backgroundColor = '';
                    elem.style.opacity = '';
                    elem.style.zIndex = '';
                });
                
                // Remove números
                var numberDivs = document.querySelectorAll('[data-highlight-number]');
                numberDivs.forEach(function(div) {
                    div.remove();
                });
            """)
        except:
            pass
            
    def run(self):
        """Executa o downloader visual"""
        print("👁️ MASTERCARD VISUAL PICKER DOWNLOADER")
        print("=" * 60)
        
        try:
            self.setup_chrome()
            self.navigate_to_announcements()
            
            selected_elements = self.highlight_and_show_clickables()
            
            if not selected_elements:
                print("❌ Nenhum elemento selecionado")
                return False
                
            downloaded_files = self.download_selected_elements(selected_elements)
            
            # Limpa destaques
            self.cleanup_highlights()
            
            # Verifica arquivos
            all_files = list(self.download_dir.glob("*"))
            
            range_start, range_end = self.get_target_date_range()
            
            print("\n" + "="*60)
            print("🎉 RESULTADO FINAL!")
            print(f"📅 Período: {range_start.strftime('%d %b')} - {range_end.strftime('%d %b %Y')}")
            print(f"🎯 Elementos selecionados: {len(selected_elements)}")
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
    downloader = VisualPickerDownloader()
    
    try:
        success = downloader.run()
        
        if success:
            print("\n🎉 DOWNLOADS REALIZADOS!")
        else:
            print("\n😔 Nenhum download foi realizado")
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo interrompido")

if __name__ == "__main__":
    main()
