#!/usr/bin/env python3
"""
Debug específico da página de Announcements
Analisa a estrutura da página de resultados
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def debug_announcements_page():
    # Setup Chrome
    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("🌐 Abrindo mastercardconnect.com...")
        driver.get("https://mastercardconnect.com")
        time.sleep(3)
        
        initial_tabs = driver.window_handles
        
        print("\n" + "="*70)
        print("🔑 Faça login e navegue para Announcements")
        print("(Deixe que o script detecte a nova aba automaticamente)")
        print("="*70)
        
        input("Pressione ENTER após clicar em Announcements...")
        
        # Detecta nova aba
        max_attempts = 10
        new_tab_found = False
        
        for attempt in range(max_attempts):
            current_tabs = driver.window_handles
            
            if len(current_tabs) > len(initial_tabs):
                new_tabs = [tab for tab in current_tabs if tab not in initial_tabs]
                newest_tab = new_tabs[-1]
                
                print(f"✅ Nova aba detectada! Trocando...")
                driver.switch_to.window(newest_tab)
                time.sleep(5)
                new_tab_found = True
                break
                
            print(f"⏳ Tentativa {attempt + 1} - Aguardando nova aba...")
            time.sleep(2)
            
        if not new_tab_found:
            print("❌ Nova aba não detectada")
            return
            
        print(f"\n🔗 URL da página: {driver.current_url}")
        print(f"📄 Título: {driver.title}")
        
        # Aguarda conteúdo carregar
        time.sleep(8)
        
        print("\n" + "="*70)
        print("🔍 ANÁLISE DETALHADA DA PÁGINA")
        print("="*70)
        
        # 1. Conta elementos básicos
        print("\n1️⃣ ELEMENTOS BÁSICOS:")
        elements = {
            'divs': len(driver.find_elements(By.TAG_NAME, "div")),
            'spans': len(driver.find_elements(By.TAG_NAME, "span")), 
            'links': len(driver.find_elements(By.TAG_NAME, "a")),
            'paragraphs': len(driver.find_elements(By.TAG_NAME, "p")),
            'headers': len(driver.find_elements(By.XPATH, "//h1 | //h2 | //h3 | //h4 | //h5 | //h6")),
            'tables': len(driver.find_elements(By.TAG_NAME, "table")),
            'lists': len(driver.find_elements(By.TAG_NAME, "ul")) + len(driver.find_elements(By.TAG_NAME, "ol"))
        }
        
        for elem_type, count in elements.items():
            print(f"   {elem_type}: {count}")
            
        # 2. Procura por texto específico
        print("\n2️⃣ TEXTOS ESPECÍFICOS:")
        search_terms = ['Publication', 'Date', '2025', '2024', 'Jun', 'Jul', 'Download']
        
        for term in search_terms:
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{term}')]")
            print(f"   '{term}': {len(elements)} elementos")
            
            # Mostra alguns exemplos
            for i, elem in enumerate(elements[:3]):
                text = elem.text.strip()[:80]
                if text:
                    print(f"      {i+1}. {text}...")
                    
        # 3. Procura estruturas de dados
        print("\n3️⃣ ESTRUTURAS DE DADOS:")
        
        # Procura por containers comuns
        containers = [
            ('.result', 'Resultados'),
            ('.item', 'Items'),
            ('.card', 'Cards'),
            ('.announcement', 'Announcements'),
            ('.document', 'Documentos'),
            ('[class*="result"]', 'Classes com "result"'),
            ('[class*="item"]', 'Classes com "item"'),
            ('[class*="card"]', 'Classes com "card"'),
            ('[data-*]', 'Elementos com data-*')
        ]
        
        for selector, description in containers:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"   {description}: {len(elements)} elementos")
                    
                    # Mostra conteúdo do primeiro
                    if elements and elements[0].text.strip():
                        sample_text = elements[0].text.strip()[:100]
                        print(f"      Exemplo: {sample_text}...")
            except:
                continue
                
        # 4. Análise de JavaScript/carregamento dinâmico
        print("\n4️⃣ CONTEÚDO DINÂMICO:")
        
        # Aguarda mais tempo para conteúdo JS
        print("   Aguardando 10 segundos para conteúdo JavaScript...")
        time.sleep(10)
        
        # Recount após espera
        new_elements = len(driver.find_elements(By.XPATH, "//*[contains(text(), '2025') or contains(text(), '2024')]"))
        print(f"   Elementos com anos após espera: {new_elements}")
        
        # 5. Salva HTML
        print("\n5️⃣ SALVANDO HTML:")
        with open('announcements_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("   ✅ HTML salvo em: announcements_page_source.html")
        
        # 6. Screenshot
        print("\n6️⃣ SCREENSHOT:")
        driver.save_screenshot('announcements_page_screenshot.png')
        print("   ✅ Screenshot salvo em: announcements_page_screenshot.png")
        
        # 7. Busca interativa
        print("\n7️⃣ BUSCA INTERATIVA:")
        print("Comandos: 'text <termo>', 'css <seletor>', 'xpath <xpath>', 'quit'")
        
        while True:
            try:
                command = input("\n> ").strip()
                
                if command == 'quit':
                    break
                elif command.startswith('text '):
                    term = command[5:]
                    elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{term}')]")
                    print(f"Encontrados {len(elements)} elementos com '{term}':")
                    for i, elem in enumerate(elements[:8]):
                        text = elem.text.strip()[:100]
                        if text:
                            print(f"  {i+1}. {text}...")
                            
                elif command.startswith('css '):
                    selector = command[4:]
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        print(f"Encontrados {len(elements)} elementos:")
                        for i, elem in enumerate(elements[:5]):
                            text = elem.text.strip()[:100]
                            print(f"  {i+1}. {text}...")
                    except Exception as e:
                        print(f"Erro: {e}")
                        
                elif command.startswith('xpath '):
                    xpath = command[6:]
                    try:
                        elements = driver.find_elements(By.XPATH, xpath)
                        print(f"Encontrados {len(elements)} elementos:")
                        for i, elem in enumerate(elements[:5]):
                            text = elem.text.strip()[:100]
                            print(f"  {i+1}. {text}...")
                    except Exception as e:
                        print(f"Erro: {e}")
                else:
                    print("Comando não reconhecido")
                    
            except KeyboardInterrupt:
                break
                
        print("\n✅ Debug finalizado!")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_announcements_page()
