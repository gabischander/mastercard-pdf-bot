#!/usr/bin/env python3
"""
Mastercard Site Explorer
Script para explorar a estrutura do site após login manual
"""

import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class MastercardExplorer:
    def __init__(self):
        self.driver = None
        
    def setup_chrome(self):
        """Configura o Chrome para usar o perfil do usuário"""
        chrome_options = Options()
        
        # Usar perfil do usuário (onde está o 1Password)
        user_data_dir = "/Users/gabrielaschander/Library/Application Support/Google/Chrome"
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--profile-directory=Default")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def open_site(self):
        """Abre o site Mastercard"""
        print("Abrindo mastercardconnect.com...")
        self.driver.get("https://mastercardconnect.com")
        
        # Aguarda página carregar
        time.sleep(3)
        
        print("✅ Site carregado!")
        print("🔑 Faça login manualmente usando o 1Password")
        input("Pressione ENTER quando estiver logado...")
        
    def find_technical_resource_center(self):
        """Procura pelo Technical Resource Center"""
        print("\n🔍 Procurando Technical Resource Center...")
        
        # Lista de possíveis seletores
        selectors = [
            "//a[contains(text(), 'Technical')]",
            "//a[contains(text(), 'Resource')]", 
            "//a[contains(text(), 'Center')]",
            "//a[contains(text(), 'TRC')]",
            "//span[contains(text(), 'Technical')]",
            "//span[contains(text(), 'Resource')]",
            "//div[contains(text(), 'Technical')]",
            "//div[contains(text(), 'Resource')]"
        ]
        
        found_elements = []
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    text = element.text.strip()
                    if text and len(text) > 0:
                        found_elements.append({
                            'element': element,
                            'text': text,
                            'tag': element.tag_name,
                            'selector': selector
                        })
                        print(f"  ✓ Encontrado: '{text}' ({element.tag_name})")
            except:
                continue
                
        if not found_elements:
            print("❌ Nenhum elemento relacionado ao Technical Resource Center encontrado")
            return False
            
        # Tenta clicar no primeiro elemento que parece ser um link
        print(f"\n📋 Encontrados {len(found_elements)} elementos relacionados")
        
        for i, elem in enumerate(found_elements):
            print(f"{i+1}. {elem['text']} ({elem['tag']})")
            
        choice = input(f"\nEscolha qual elemento clicar (1-{len(found_elements)}) ou 0 para pular: ")
        
        try:
            choice = int(choice)
            if choice == 0:
                return False
            if 1 <= choice <= len(found_elements):
                selected = found_elements[choice-1]
                print(f"Clicando em: {selected['text']}")
                self.driver.execute_script("arguments[0].click();", selected['element'])
                time.sleep(3)
                return True
        except:
            pass
            
        return False
        
    def find_announcements(self):
        """Procura pela seção Announcements"""
        print("\n🔍 Procurando Announcements...")
        
        # Lista de possíveis seletores
        selectors = [
            "//a[contains(text(), 'Announcement')]",
            "//a[contains(text(), 'Anúncio')]",
            "//span[contains(text(), 'Announcement')]",
            "//div[contains(text(), 'Announcement')]",
            "//h1[contains(text(), 'Announcement')]",
            "//h2[contains(text(), 'Announcement')]",
            "//h3[contains(text(), 'Announcement')]"
        ]
        
        found_elements = []
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    text = element.text.strip()
                    if text and len(text) > 0:
                        found_elements.append({
                            'element': element,
                            'text': text,
                            'tag': element.tag_name,
                            'selector': selector
                        })
                        print(f"  ✓ Encontrado: '{text}' ({element.tag_name})")
            except:
                continue
                
        if not found_elements:
            print("❌ Nenhum elemento relacionado ao Announcements encontrado")
            return False
            
        # Tenta clicar no primeiro elemento que parece ser um link
        print(f"\n📋 Encontrados {len(found_elements)} elementos relacionados")
        
        for i, elem in enumerate(found_elements):
            print(f"{i+1}. {elem['text']} ({elem['tag']})")
            
        choice = input(f"\nEscolha qual elemento clicar (1-{len(found_elements)}) ou 0 para pular: ")
        
        try:
            choice = int(choice)
            if choice == 0:
                return False
            if 1 <= choice <= len(found_elements):
                selected = found_elements[choice-1]
                print(f"Clicando em: {selected['text']}")
                self.driver.execute_script("arguments[0].click();", selected['element'])
                time.sleep(3)
                return True
        except:
            pass
            
        return False
        
    def analyze_page_structure(self):
        """Analisa a estrutura da página atual"""
        print(f"\n📊 Analisando página atual: {self.driver.current_url}")
        
        # Procura por elementos com datas
        print("\n🗓️ Procurando elementos com datas...")
        date_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '2024') or contains(text(), '2025') or contains(text(), 'Jun') or contains(text(), 'Jul') or contains(text(), 'Date')]")
        
        if date_elements:
            print(f"  ✓ Encontrados {len(date_elements)} elementos com possíveis datas:")
            for i, elem in enumerate(date_elements[:10]):  # Mostra apenas os primeiros 10
                text = elem.text.strip()
                if text:
                    print(f"    {i+1}. {text[:100]}...")
        else:
            print("  ❌ Nenhum elemento com data encontrado")
            
        # Procura por elementos de download
        print("\n📥 Procurando elementos de download...")
        download_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Download') or contains(@href, 'download') or contains(@href, '.zip') or contains(@href, '.pdf')]")
        
        if download_elements:
            print(f"  ✓ Encontrados {len(download_elements)} elementos de download:")
            for i, elem in enumerate(download_elements[:10]):  # Mostra apenas os primeiros 10
                text = elem.text.strip()
                href = elem.get_attribute('href') or ''
                if text or href:
                    print(f"    {i+1}. {text or href[:100]}...")
        else:
            print("  ❌ Nenhum elemento de download encontrado")
            
        # Procura por tabelas ou listas
        print("\n📋 Procurando estruturas de dados...")
        tables = self.driver.find_elements(By.TAG_NAME, "table")
        if tables:
            print(f"  ✓ Encontradas {len(tables)} tabelas")
            
        lists = self.driver.find_elements(By.TAG_NAME, "ul")
        if lists:
            print(f"  ✓ Encontradas {len(lists)} listas")
            
        # Procura por cards ou containers
        cards = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'card') or contains(@class, 'item') or contains(@class, 'announcement')]")
        if cards:
            print(f"  ✓ Encontrados {len(cards)} cards/containers")
            
    def get_previous_week_range(self):
        """Calcula o range da semana anterior"""
        today = datetime.now()
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        print(f"\n📅 Semana anterior: {last_monday.strftime('%d %b %Y')} até {last_sunday.strftime('%d %b %Y')}")
        return last_monday, last_sunday
        
    def interactive_navigation(self):
        """Navegação interativa para explorar o site"""
        print("\n🧭 Modo de navegação interativa")
        print("Digite 'quit' para sair")
        
        while True:
            action = input("\nAção (url/click/analyze/back/quit): ").strip().lower()
            
            if action == 'quit':
                break
            elif action == 'url':
                url = input("Digite a URL: ")
                try:
                    self.driver.get(url)
                    time.sleep(2)
                    print(f"✅ Navegou para: {self.driver.current_url}")
                except Exception as e:
                    print(f"❌ Erro: {e}")
            elif action == 'click':
                text = input("Digite o texto do elemento para clicar: ")
                try:
                    element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
                    self.driver.execute_script("arguments[0].click();", element)
                    time.sleep(2)
                    print(f"✅ Clicou em elemento com texto: {text}")
                except Exception as e:
                    print(f"❌ Erro: {e}")
            elif action == 'analyze':
                self.analyze_page_structure()
            elif action == 'back':
                try:
                    self.driver.back()
                    time.sleep(2)
                    print("✅ Voltou para página anterior")
                except Exception as e:
                    print(f"❌ Erro: {e}")
            else:
                print("Ações disponíveis: url, click, analyze, back, quit")
                
    def run_exploration(self):
        """Executa a exploração do site"""
        print("🚀 Iniciando exploração do site Mastercard")
        
        try:
            # Configura navegador
            self.setup_chrome()
            
            # Abre site
            self.open_site()
            
            # Calcula semana anterior
            self.get_previous_week_range()
            
            # Procura Technical Resource Center
            if self.find_technical_resource_center():
                print("✅ Navegou para Technical Resource Center")
                
                # Procura Announcements
                if self.find_announcements():
                    print("✅ Navegou para Announcements")
                    
                    # Analisa estrutura
                    self.analyze_page_structure()
                else:
                    print("⚠️ Não encontrou Announcements, analisando página atual")
                    self.analyze_page_structure()
            else:
                print("⚠️ Não encontrou Technical Resource Center")
                
            # Navegação interativa
            self.interactive_navigation()
            
        except Exception as e:
            print(f"❌ Erro durante exploração: {e}")
            
        finally:
            if self.driver:
                self.driver.quit()
                print("🔚 Navegador fechado")

def main():
    explorer = MastercardExplorer()
    explorer.run_exploration()

if __name__ == "__main__":
    main()
