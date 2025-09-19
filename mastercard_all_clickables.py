#!/usr/bin/env python3
"""
Mastercard All Clickables Downloader
Procura TODOS os elementos clicáveis e verifica quais estão próximos das datas
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

class AllClickablesDownloader:
    def __init__(self):
        self.download_dir = Path("downloads_all_clickables")
        self.pdf_dir = Path("pdfs_all_clickables")
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
        
    def find_all_clickables_near_dates(self):
        """Encontra TODOS os elementos clicáveis e verifica proximidade com datas"""
        print(f"\n🔍 Procurando TODOS os elementos clicáveis...")
        
        range_start, range_end = self.get_target_date_range()
        
        # 1. Encontra todos os elementos clicáveis da página
        all_clickables = []
        
        selectors = [
            '//a', '//button', '//*[@onclick]', '//*[@role="button"]',
            '//i', '//svg', '//*[contains(@class, "icon")]', 
            '//*[contains(@class, "btn")]', '//*[contains(@class, "click")]'
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                all_clickables.extend(elements)
            except:
                continue
                
        # Remove duplicatas
        unique_clickables = []
        for elem in all_clickables:
            if elem not in unique_clickables:
                unique_clickables.append(elem)
                
        print(f"📋 Total de elementos clicáveis únicos: {len(unique_clickables)}")
        
        # 2. Para cada elemento clicável, verifica se está próximo a uma data válida
        valid_downloads = []
        
        for i, clickable in enumerate(unique_clickables):
            try:
                if i % 10 == 0:
                    print(f"   📊 Analisando elementos {i+1}-{min(i+10, len(unique_clickables))}/{len(unique_clickables)}...")
                
                # Verifica se está próximo a uma data válida
                date_info = self.find_nearby_date(clickable, range_start, range_end)
                
                if date_info:
                    # Pontua este elemento como candidato a download
                    score = self.score_download_candidate(clickable)
                    
                    if score > 0:
                        valid_downloads.append({
                            'clickable': clickable,
                            'date': date_info['date'],
                            'date_str': date_info['date_str'],
                            'score': score,
                            'context': self.get_context(clickable)
                        })
                        
            except:
                continue
                
        print(f"📋 Elementos clicáveis próximos a datas válidas: {len(valid_downloads)}")
        
        # 3. Ordena por score e remove duplicatas por contexto
        if valid_downloads:
            # Ordena por score decrescente
            valid_downloads.sort(key=lambda x: x['score'], reverse=True)
            
            print("🎯 Top candidatos:")
            for i, item in enumerate(valid_downloads[:10]):
                print(f"   {i+1}. Score: {item['score']} | Data: {item['date_str']} | Contexto: {item['context'][:40]}...")
                
            # Remove duplicatas por contexto similar
            unique_downloads = []
            seen_contexts = set()
            
            for item in valid_downloads:
                context_key = item['context'][:100].lower().strip()
                if context_key not in seen_contexts:
                    unique_downloads.append(item)
                    seen_contexts.add(context_key)
                    
            print(f"\n📋 Downloads únicos após remoção de duplicatas: {len(unique_downloads)}")
            
            return unique_downloads[:5]  # Máximo 5 downloads
            
        return []
        
    def find_nearby_date(self, element, range_start, range_end):
        """Procura por datas próximas ao elemento"""
        try:
            # Estratégia: sobe na hierarquia procurando por datas
            current = element
            
            for level in range(15):
                try:
                    if level > 0:
                        current = current.find_element(By.XPATH, "./..")
                    
                    text = current.text.strip()
                    
                    # Procura padrões de data no texto
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
                                        'date_str': date_obj.strftime('%d %b %Y'),
                                        'level': level
                                    }
                                    
                            except ValueError:
                                continue
                                
                except:
                    break
                    
            return None
            
        except:
            return None
            
    def score_download_candidate(self, element):
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
            
            # Pontuação alta para palavras-chave obvias
            if 'download' in all_text: score += 10
            if 'zip' in all_text: score += 8
            if 'pdf' in all_text: score += 8
            if 'file' in all_text: score += 5
            if 'export' in all_text: score += 5
            if 'save' in all_text: score += 3
            if 'arrow' in all_text: score += 3
            
            # Pontuação por tipo de elemento
            if tag == 'a' and href: score += 5
            if tag == 'button': score += 4
            if onclick: score += 4
            if tag in ['i', 'svg']: score += 3
            
            # Bonificação por classes específicas
            if 'btn' in classes: score += 2
            if 'icon' in classes: score += 2
            if 'click' in classes: score += 2
            
            # Penalização por muito texto (não deve ser ícone)
            if len(text) > 20: score -= 3
            if len(text) > 50: score -= 5
            
            # Penalização por elementos muito pequenos (podem ser invisíveis)
            try:
                rect = element.rect
                if rect:
                    if rect['width'] < 5 or rect['height'] < 5:
                        score -= 5
                    elif 10 <= rect['width'] <= 80 and 10 <= rect['height'] <= 80:
                        score += 2  # Tamanho ideal para ícone
                        
            except:
                pass
                
        except:
            pass
            
        return max(0, score)
        
    def get_context(self, element):
        """Pega contexto ao redor do elemento"""
        try:
            # Tenta pegar texto do elemento pai
            for level in range(5):
                try:
                    if level == 0:
                        current = element
                    else:
                        current = element
                        for _ in range(level):
                            current = current.find_element(By.XPATH, "./..")
                            
                    text = current.text.strip()
                    if len(text) > 30:
                        return text[:100]
                        
                except:
                    continue
                    
            return element.text.strip()[:50] or "Sem contexto"
            
        except:
            return "Sem contexto"
            
    def download_elements(self, download_items):
        """Tenta fazer download dos elementos"""
        if not download_items:
            print("❌ Nenhum elemento para download")
            return []
            
        print(f"\n📥 Tentando downloads de {len(download_items)} elementos...")
        
        downloaded_files = []
        actions = ActionChains(self.driver)
        
        for i, item in enumerate(download_items):
            try:
                print(f"\n📥 Tentativa {i+1}/{len(download_items)}:")
                print(f"   📊 Score: {item['score']}")
                print(f"   📅 Data: {item['date_str']}")
                print(f"   📄 Contexto: {item['context'][:60]}...")
                
                # Scroll para o elemento
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item['clickable'])
                time.sleep(2)
                
                # Destaca elemento
                self.driver.execute_script(
                    "arguments[0].style.border='4px solid red'; arguments[0].style.backgroundColor='yellow'; arguments[0].style.zIndex='9999';", 
                    item['clickable']
                )
                time.sleep(2)
                
                print("   🖱️ Clicando...")
                
                # Tenta clicar
                clicked = False
                try:
                    item['clickable'].click()
                    clicked = True
                    print("      ✅ Clique direto")
                except:
                    try:
                        self.driver.execute_script("arguments[0].click();", item['clickable'])
                        clicked = True
                        print("      ✅ Clique JavaScript")
                    except:
                        try:
                            actions.move_to_element(item['clickable']).click().perform()
                            clicked = True
                            print("      ✅ ActionChains")
                        except Exception as e:
                            print(f"      ❌ Falha: {e}")
                
                # Remove destaque
                self.driver.execute_script(
                    "arguments[0].style.border=''; arguments[0].style.backgroundColor=''; arguments[0].style.zIndex='';", 
                    item['clickable']
                )
                
                if clicked:
                    print("   ⏳ Aguardando possível download...")
                    
                    # Aguarda um pouco para ver se algo acontece
                    time.sleep(5)
                    
                    # Verifica se houve download
                    downloaded_file = self.check_for_download()
                    
                    if downloaded_file:
                        downloaded_files.append({
                            'file': downloaded_file,
                            'date_str': item['date_str'],
                            'score': item['score'],
                            'context': item['context']
                        })
                        print(f"   ✅ Download detectado: {downloaded_file.name}")
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
            
            # Procura por arquivos recentes
            for file in files:
                if file.is_file():
                    # Verifica se é um arquivo recente (últimos 10 segundos)
                    file_time = file.stat().st_mtime
                    current_time = time.time()
                    
                    if current_time - file_time < 10:  # Arquivo dos últimos 10 segundos
                        return file
                        
            return None
            
        except:
            return None
            
    def run(self):
        """Executa o downloader"""
        print("🎯 MASTERCARD ALL CLICKABLES DOWNLOADER")
        print("=" * 60)
        
        try:
            self.setup_chrome()
            self.navigate_to_announcements()
            
            download_items = self.find_all_clickables_near_dates()
            
            if not download_items:
                print("❌ Nenhum elemento clicável próximo a datas válidas")
                return False
                
            downloaded_files = self.download_elements(download_items)
            
            # Verifica todos os arquivos baixados
            all_files = list(self.download_dir.glob("*"))
            
            range_start, range_end = self.get_target_date_range()
            
            print("\n" + "="*60)
            print("🎉 RESULTADO FINAL!")
            print(f"📅 Período: {range_start.strftime('%d %b')} - {range_end.strftime('%d %b %Y')}")
            print(f"🎯 Elementos processados: {len(download_items)}")
            print(f"📥 Downloads detectados: {len(downloaded_files)}")
            print(f"📁 Arquivos na pasta: {len(all_files)}")
            
            if all_files:
                print(f"\n📁 ARQUIVOS ENCONTRADOS:")
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
    downloader = AllClickablesDownloader()
    
    try:
        success = downloader.run()
        
        if success:
            print("\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
        else:
            print("\n😔 Nenhum download foi realizado")
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo interrompido")

if __name__ == "__main__":
    main()
