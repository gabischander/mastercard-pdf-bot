#!/usr/bin/env python3
"""
Debug da estrutura da página de Announcements
Para entender como os elementos estão organizados
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class PageDebugger:
    def __init__(self):
        self.driver = None
        
    def setup_chrome(self):
        """Configura Chrome"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def open_and_wait(self):
        """Abre site e aguarda navegação manual"""
        print("🌐 Abrindo mastercardconnect.com...")
        self.driver.get("https://mastercardconnect.com")
        time.sleep(3)
        
        print("\n" + "="*60)
        print("🔑 Faça login e navegue para Announcements")
        print("="*60)
        input("Pressione ENTER quando estiver na página de Announcements...")
        
    def debug_page_content(self):
        """Analisa o conteúdo da página em detalhes"""
        print(f"\n🔍 DEBUGANDO PÁGINA: {self.driver.current_url}")
        print("=" * 80)
        
        # Aguarda conteúdo carregar
        time.sleep(5)
        
        # 1. Procura por qualquer menção a "Publication"
        print("\n1️⃣ PROCURANDO POR 'Publication':")
        pub_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Publication')]")
        print(f"   Encontrados: {len(pub_elements)} elementos")
        
        for i, elem in enumerate(pub_elements[:5]):  # Primeiros 5
            text = elem.text.strip()
            tag = elem.tag_name
            print(f"   {i+1}. [{tag}] {text[:100]}...")
            
        # 2. Procura por qualquer menção a "Date"
        print("\n2️⃣ PROCURANDO POR 'Date':")
        date_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Date')]")
        print(f"   Encontrados: {len(date_elements)} elementos")
        
        for i, elem in enumerate(date_elements[:5]):  # Primeiros 5
            text = elem.text.strip()
            tag = elem.tag_name
            print(f"   {i+1}. [{tag}] {text[:100]}...")
            
        # 3. Procura por datas no formato "1 Jul 2025"
        print("\n3️⃣ PROCURANDO POR DATAS (formato: 1 Jul 2025):")
        date_pattern_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Jul 2025') or contains(text(), 'Jun 2025')]")
        print(f"   Encontrados: {len(date_pattern_elements)} elementos")
        
        for i, elem in enumerate(date_pattern_elements[:10]):  # Primeiros 10
            text = elem.text.strip()
            tag = elem.tag_name
            print(f"   {i+1}. [{tag}] {text[:150]}...")
            
        # 4. Procura por botões/ícones de download
        print("\n4️⃣ PROCURANDO POR DOWNLOADS:")
        download_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Download') or contains(@href, 'download') or contains(@href, '.zip')]")
        print(f"   Encontrados: {len(download_elements)} elementos")
        
        for i, elem in enumerate(download_elements[:5]):  # Primeiros 5
            text = elem.text.strip() or elem.get_attribute('href') or 'N/A'
            tag = elem.tag_name
            print(f"   {i+1}. [{tag}] {text[:100]}...")
            
        # 5. Analisa estrutura geral da página
        print("\n5️⃣ ESTRUTURA GERAL:")
        
        # Título da página
        print(f"   Título: {self.driver.title}")
        
        # Elementos principais
        main_elements = {
            'tables': len(self.driver.find_elements(By.TAG_NAME, "table")),
            'divs': len(self.driver.find_elements(By.TAG_NAME, "div")),
            'spans': len(self.driver.find_elements(By.TAG_NAME, "span")),
            'links': len(self.driver.find_elements(By.TAG_NAME, "a")),
            'buttons': len(self.driver.find_elements(By.TAG_NAME, "button")),
            'images': len(self.driver.find_elements(By.TAG_NAME, "img"))
        }
        
        for elem_type, count in main_elements.items():
            print(f"   {elem_type}: {count}")
            
        # 6. Procura por elementos que podem conter documentos
        print("\n6️⃣ CONTAINERS DE DOCUMENTOS:")
        container_selectors = [
            '//*[contains(@class, "item")]',
            '//*[contains(@class, "card")]', 
            '//*[contains(@class, "document")]',
            '//*[contains(@class, "announcement")]',
            '//*[contains(@class, "row")]',
            '//*[contains(@class, "list")]'
        ]
        
        for selector in container_selectors:
            elements = self.driver.find_elements(By.XPATH, selector)
            if elements:
                print(f"   {selector}: {len(elements)} elementos")
                
                # Mostra conteúdo do primeiro elemento
                if elements:
                    first_elem = elements[0]
                    print(f"      Exemplo: {first_elem.text[:200]}...")
                    
        # 7. Salva HTML da página para análise
        print("\n7️⃣ SALVANDO HTML:")
        with open('debug_page_source.html', 'w', encoding='utf-8') as f:
            f.write(self.driver.page_source)
        print("   HTML salvo em: debug_page_source.html")
        
    def interactive_search(self):
        """Interface interativa para buscar elementos"""
        print("\n🔧 MODO INTERATIVO")
        print("Comandos:")
        print("  'search <texto>' - Busca por texto")
        print("  'xpath <xpath>' - Busca por XPath")  
        print("  'css <seletor>' - Busca por CSS")
        print("  'quit' - Sair")
        
        while True:
            try:
                command = input("\n> ").strip()
                
                if command == 'quit':
                    break
                elif command.startswith('search '):
                    text = command[7:]
                    elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
                    print(f"Encontrados {len(elements)} elementos com '{text}':")
                    for i, elem in enumerate(elements[:5]):
                        print(f"  {i+1}. [{elem.tag_name}] {elem.text[:100]}...")
                        
                elif command.startswith('xpath '):
                    xpath = command[6:]
                    try:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        print(f"Encontrados {len(elements)} elementos:")
                        for i, elem in enumerate(elements[:5]):
                            print(f"  {i+1}. [{elem.tag_name}] {elem.text[:100]}...")
                    except Exception as e:
                        print(f"Erro no XPath: {e}")
                        
                elif command.startswith('css '):
                    css = command[4:]
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, css)
                        print(f"Encontrados {len(elements)} elementos:")
                        for i, elem in enumerate(elements[:5]):
                            print(f"  {i+1}. [{elem.tag_name}] {elem.text[:100]}...")
                    except Exception as e:
                        print(f"Erro no CSS: {e}")
                else:
                    print("Comando não reconhecido")
                    
            except KeyboardInterrupt:
                break
                
    def run_debug(self):
        """Executa debug completo"""
        print("🐛 DEBUG DA ESTRUTURA DA PÁGINA MASTERCARD")
        print("=" * 80)
        
        try:
            self.setup_chrome()
            self.open_and_wait()
            self.debug_page_content()
            self.interactive_search()
            
        except Exception as e:
            print(f"❌ Erro durante debug: {e}")
            
        finally:
            if self.driver:
                self.driver.quit()
                print("\n🔚 Debug finalizado")

def main():
    debugger = PageDebugger()
    debugger.run_debug()

if __name__ == "__main__":
    main()
