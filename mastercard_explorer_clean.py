#!/usr/bin/env python3
"""
Mastercard Site Explorer - Chrome limpo
Script para explorar a estrutura do site após login manual
"""

import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class MastercardExplorer:
    def __init__(self):
        self.driver = None
        
    def setup_chrome(self):
        """Configura o Chrome limpo"""
        chrome_options = Options()
        
        # Configurações básicas
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def open_site(self):
        """Abre o site Mastercard"""
        print("Abrindo mastercardconnect.com...")
        self.driver.get("https://mastercardconnect.com")
        
        # Aguarda página carregar
        time.sleep(3)
        
        print("✅ Site carregado!")
        print("🔑 Faça login manualmente nesta janela")
        print("   Use suas credenciais: gabriela.braga@cloudwalk.io")
        input("Pressione ENTER quando estiver logado...")
        
    def search_for_text(self, text_list):
        """Procura por textos específicos na página"""
        found_elements = []
        
        for text in text_list:
            try:
                # Busca por text exato
                elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
                for element in elements:
                    elem_text = element.text.strip()
                    if elem_text and len(elem_text) > 0:
                        found_elements.append({
                            'element': element,
                            'text': elem_text,
                            'tag': element.tag_name,
                            'search_term': text
                        })
            except:
                continue
                
        return found_elements
        
    def find_navigation_elements(self):
        """Procura por elementos de navegação"""
        print("\n🔍 Procurando elementos de navegação...")
        
        search_terms = [
            'Technical', 'Resource', 'Center', 'TRC',
            'Announcement', 'Anúncio', 'Documents', 'Documentos',
            'Reports', 'Relatórios', 'Publications', 'Publicações'
        ]
        
        found_elements = self.search_for_text(search_terms)
        
        if found_elements:
            print(f"✓ Encontrados {len(found_elements)} elementos de navegação:")
            for i, elem in enumerate(found_elements):
                print(f"  {i+1}. '{elem['text'][:50]}...' ({elem['tag']}) - busca: {elem['search_term']}")
        else:
            print("❌ Nenhum elemento de navegação encontrado")
            
        return found_elements
        
    def analyze_current_page(self):
        """Analisa a página atual em detalhes"""
        print(f"\n📊 Analisando página: {self.driver.current_url}")
        print(f"📄 Título: {self.driver.title}")
        
        # Procura por elementos com datas
        print("\n🗓️ Elementos com datas:")
        date_patterns = ['2024', '2025', 'Jun', 'Jul', 'Aug', 'Date', 'Publication']
        date_elements = []
        
        for pattern in date_patterns:
            elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{pattern}')]")
            for elem in elements:
                text = elem.text.strip()
                if text and len(text) < 200:  # Evita textos muito longos
                    date_elements.append({'text': text, 'pattern': pattern})
                    
        if date_elements:
            print(f"  ✓ Encontrados {len(date_elements)} elementos:")
            for i, elem in enumerate(date_elements[:15]):  # Primeiros 15
                print(f"    {i+1}. {elem['text']} (padrão: {elem['pattern']})")
        else:
            print("  ❌ Nenhum elemento com data encontrado")
            
        # Procura por downloads
        print("\n📥 Elementos de download:")
        download_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Download') or contains(@href, 'download') or contains(@href, '.zip') or contains(@href, '.pdf') or contains(text(), 'ZIP')]")
        
        if download_elements:
            print(f"  ✓ Encontrados {len(download_elements)} elementos:")
            for i, elem in enumerate(download_elements[:10]):
                text = elem.text.strip() or elem.get_attribute('href') or 'N/A'
                print(f"    {i+1}. {text[:60]}...")
        else:
            print("  ❌ Nenhum elemento de download encontrado")
            
        # Procura por estruturas de lista/tabela
        print("\n📋 Estruturas de dados:")
        tables = self.driver.find_elements(By.TAG_NAME, "table")
        lists = self.driver.find_elements(By.TAG_NAME, "ul")
        divs_with_class = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'item') or contains(@class, 'card') or contains(@class, 'list') or contains(@class, 'row')]")
        
        print(f"  ✓ Tabelas: {len(tables)}")
        print(f"  ✓ Listas: {len(lists)}")
        print(f"  ✓ Divs estruturados: {len(divs_with_class)}")
        
        # Analisa links principais
        print("\n🔗 Links principais:")
        links = self.driver.find_elements(By.TAG_NAME, "a")
        important_links = []
        
        for link in links:
            href = link.get_attribute('href')
            text = link.text.strip()
            if href and text and len(text) > 3:
                important_links.append({'text': text, 'href': href})
                
        if important_links:
            print(f"  ✓ Encontrados {len(important_links)} links:")
            for i, link in enumerate(important_links[:15]):  # Primeiros 15
                print(f"    {i+1}. {link['text'][:40]}... -> {link['href'][:60]}...")
        
    def interactive_navigation(self):
        """Interface interativa para navegar"""
        print("\n🧭 Navegação Interativa")
        print("Comandos disponíveis:")
        print("  'analyze' - Analisa a página atual")
        print("  'click <texto>' - Clica em elemento com texto")
        print("  'url <url>' - Navega para URL")
        print("  'back' - Volta para página anterior")
        print("  'search <termo>' - Busca por termo na página")
        print("  'week' - Mostra datas da semana anterior")
        print("  'quit' - Sair")
        
        while True:
            try:
                command = input("\n> ").strip()
                
                if command == 'quit':
                    break
                elif command == 'analyze':
                    self.analyze_current_page()
                elif command.startswith('click '):
                    text = command[6:].strip()
                    self.click_element_with_text(text)
                elif command.startswith('url '):
                    url = command[4:].strip()
                    self.navigate_to_url(url)
                elif command == 'back':
                    self.go_back()
                elif command.startswith('search '):
                    term = command[7:].strip()
                    self.search_page_for_term(term)
                elif command == 'week':
                    self.show_previous_week()
                else:
                    print("❌ Comando não reconhecido")
                    
            except KeyboardInterrupt:
                break
                
    def click_element_with_text(self, text):
        """Clica em elemento com texto específico"""
        try:
            element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
            self.driver.execute_script("arguments[0].click();", element)
            time.sleep(2)
            print(f"✅ Clicou no elemento: {text}")
        except Exception as e:
            print(f"❌ Erro ao clicar: {e}")
            
    def navigate_to_url(self, url):
        """Navega para URL específica"""
        try:
            if not url.startswith('http'):
                url = 'https://' + url
            self.driver.get(url)
            time.sleep(2)
            print(f"✅ Navegou para: {self.driver.current_url}")
        except Exception as e:
            print(f"❌ Erro na navegação: {e}")
            
    def go_back(self):
        """Volta para página anterior"""
        try:
            self.driver.back()
            time.sleep(2)
            print("✅ Voltou para página anterior")
        except Exception as e:
            print(f"❌ Erro ao voltar: {e}")
            
    def search_page_for_term(self, term):
        """Busca por termo na página atual"""
        try:
            elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{term}')]")
            print(f"🔍 Encontrados {len(elements)} elementos com '{term}':")
            for i, elem in enumerate(elements[:10]):
                text = elem.text.strip()[:60]
                print(f"  {i+1}. {text}... ({elem.tag_name})")
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            
    def show_previous_week(self):
        """Mostra as datas da semana anterior"""
        today = datetime.now()
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        print(f"📅 Semana anterior:")
        print(f"   Início: {last_monday.strftime('%d %b %Y')} (segunda)")
        print(f"   Fim: {last_sunday.strftime('%d %b %Y')} (domingo)")
        print(f"   Formato curto: {last_monday.strftime('%d %b')} - {last_sunday.strftime('%d %b')}")
        
    def run_exploration(self):
        """Executa a exploração completa"""
        print("🚀 Iniciando Exploração do Site Mastercard")
        print("===========================================")
        
        try:
            # Configura Chrome
            self.setup_chrome()
            
            # Abre site
            self.open_site()
            
            # Mostra informações da semana
            self.show_previous_week()
            
            # Analisa página inicial
            print("\n📊 Análise inicial da página:")
            self.analyze_current_page()
            
            # Procura elementos de navegação
            nav_elements = self.find_navigation_elements()
            
            if nav_elements:
                print(f"\n🎯 Elementos para explorar:")
                for i, elem in enumerate(nav_elements[:10]):
                    print(f"  {i+1}. {elem['text'][:50]}...")
                    
                # Sugestões automáticas
                print("\n💡 Sugestões:")
                print("   - Digite 'click Technical' para ir ao Technical Resource Center")
                print("   - Digite 'click Announcement' para ir aos Announcements")
                print("   - Digite 'search Publication' para buscar por publicações")
                
            # Inicia navegação interativa
            self.interactive_navigation()
            
        except Exception as e:
            print(f"❌ Erro durante exploração: {e}")
            
        finally:
            if self.driver:
                self.driver.quit()
                print("\n🔚 Exploração finalizada")

def main():
    explorer = MastercardExplorer()
    explorer.run_exploration()

if __name__ == "__main__":
    main()
