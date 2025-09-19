#!/usr/bin/env python3
"""
Debug específico para ícones de download
Analisa todos os elementos clicáveis na página
"""

import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def analyze_download_icons():
    print("🕵️ ANALISADOR DE ÍCONES DE DOWNLOAD")
    print("=" * 50)
    
    # Setup Chrome
    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("\n🌐 Abrindo mastercardconnect.com...")
        driver.get("https://mastercardconnect.com")
        time.sleep(3)
        
        print("\n" + "="*50)
        print("🎯 NAVEGAÇÃO MANUAL")
        print("1. 🔑 Faça login")
        print("2. 🏢 Vá para Technical Resource Center") 
        print("3. 📢 Clique em Announcements")
        print("=" * 50)
        
        input("Pressione ENTER quando estiver vendo os documentos...")
        
        # Verifica abas
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            
        print("\n🔍 ANÁLISE DETALHADA DA PÁGINA")
        print("=" * 50)
        
        # 1. Todos os links
        print("\n1️⃣ LINKS NA PÁGINA:")
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"   Total: {len(links)} links")
        
        for i, link in enumerate(links[:20]):  # Primeiros 20
            href = link.get_attribute('href') or 'sem href'
            title = link.get_attribute('title') or 'sem title'
            text = (link.text or '').strip()[:50]
            classes = link.get_attribute('class') or 'sem classes'
            
            if any(keyword in (href + title + text + classes).lower() 
                   for keyword in ['download', 'zip', 'pdf', 'arrow']):
                print(f"   🎯 Link {i+1}: {text} | href: {href[:50]} | title: {title}")
                
        # 2. Todos os botões
        print(f"\n2️⃣ BOTÕES NA PÁGINA:")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"   Total: {len(buttons)} botões")
        
        for i, btn in enumerate(buttons[:20]):
            onclick = btn.get_attribute('onclick') or 'sem onclick'
            title = btn.get_attribute('title') or 'sem title'
            text = (btn.text or '').strip()[:50]
            classes = btn.get_attribute('class') or 'sem classes'
            
            if any(keyword in (onclick + title + text + classes).lower() 
                   for keyword in ['download', 'zip', 'pdf', 'arrow']):
                print(f"   🎯 Botão {i+1}: {text} | onclick: {onclick[:50]} | title: {title}")
                
        # 3. Ícones (i, svg, img)
        print(f"\n3️⃣ ÍCONES NA PÁGINA:")
        
        # Ícones <i>
        icons_i = driver.find_elements(By.TAG_NAME, "i")
        print(f"   Ícones <i>: {len(icons_i)}")
        
        for i, icon in enumerate(icons_i[:15]):
            classes = icon.get_attribute('class') or 'sem classes'
            title = icon.get_attribute('title') or icon.get_attribute('aria-label') or 'sem title'
            parent_onclick = ''
            
            try:
                parent = icon.find_element(By.XPATH, "./..")
                parent_onclick = parent.get_attribute('onclick') or ''
            except:
                pass
                
            if any(keyword in (classes + title + parent_onclick).lower() 
                   for keyword in ['download', 'arrow', 'down', 'file']):
                print(f"   🎯 Ícone <i> {i+1}: classes={classes} | title={title}")
            elif 'fa-' in classes or 'icon' in classes:
                print(f"   📱 Ícone <i> {i+1}: {classes}")
                
        # SVGs
        svgs = driver.find_elements(By.TAG_NAME, "svg")
        print(f"   SVGs: {len(svgs)}")
        
        # 4. Elementos com atributos específicos
        print(f"\n4️⃣ ELEMENTOS COM ATRIBUTOS ESPECÍFICOS:")
        
        # data-*
        data_elems = driver.find_elements(By.XPATH, "//*[starts-with(@data-action, 'download') or contains(@data-action, 'download')]")
        print(f"   data-action download: {len(data_elems)}")
        
        # 5. Análise das linhas de resultado
        print(f"\n5️⃣ ESTRUTURA DOS RESULTADOS:")
        
        # Procura containers típicos de resultados
        containers = driver.find_elements(By.CSS_SELECTOR, 
            "[class*='result'], [class*='item'], [class*='row'], [class*='card'], [class*='list']")
        
        print(f"   Containers de resultado: {len(containers)}")
        
        # Para cada container, analisa se tem data e elementos clicáveis
        date_containers = []
        
        for i, container in enumerate(containers[:10]):
            text = (container.text or '').strip()
            
            # Procura por datas de junho/julho
            if any(month in text for month in ['Jun', 'Jul']) and any(day in text for day in ['25', '26', '27', '28', '29', '30', '01']):
                print(f"\n   📅 Container {i+1} com data:")
                print(f"      Texto: {text[:100]}...")
                
                # Procura elementos clicáveis dentro
                clickables = container.find_elements(By.XPATH, ".//a | .//button | .//*[@onclick]")
                print(f"      Elementos clicáveis: {len(clickables)}")
                
                for j, clickable in enumerate(clickables[:3]):
                    tag = clickable.tag_name
                    href = clickable.get_attribute('href') or ''
                    onclick = clickable.get_attribute('onclick') or ''
                    title = clickable.get_attribute('title') or ''
                    classes = clickable.get_attribute('class') or ''
                    inner_text = (clickable.text or '').strip()[:30]
                    
                    print(f"         {j+1}. <{tag}> {inner_text} | href: {href[:30]} | classes: {classes[:30]}")
                    
                date_containers.append(container)
                
        # 6. HTML de um container com data
        if date_containers:
            print(f"\n6️⃣ HTML DE UM CONTAINER COM DATA:")
            sample_container = date_containers[0]
            html = sample_container.get_attribute('outerHTML')[:1000]
            print(f"   HTML (primeiros 1000 chars):")
            print(f"   {html}")
            
        # 7. Javascript debug
        print(f"\n7️⃣ JAVASCRIPT DEBUG:")
        
        # Executa JavaScript para encontrar elementos com listeners
        js_result = driver.execute_script("""
            var elements = [];
            document.querySelectorAll('*').forEach(function(el) {
                var events = getEventListeners ? getEventListeners(el) : {};
                if (events.click || el.onclick || el.getAttribute('onclick')) {
                    var rect = el.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        elements.push({
                            tag: el.tagName,
                            classes: el.className,
                            text: el.innerText ? el.innerText.substring(0, 50) : '',
                            onclick: el.getAttribute('onclick') || '',
                            href: el.getAttribute('href') || ''
                        });
                    }
                }
            });
            return elements.slice(0, 20);
        """)
        
        print(f"   Elementos com event listeners: {len(js_result)}")
        for i, elem in enumerate(js_result):
            if any(keyword in (elem.get('classes', '') + elem.get('text', '') + elem.get('onclick', '') + elem.get('href', '')).lower() 
                   for keyword in ['download', 'arrow', 'file', 'zip', 'pdf']):
                print(f"   🎯 Elem {i+1}: <{elem['tag']}> {elem['text']} | classes: {elem['classes'][:30]}")
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        
    finally:
        input("\nPressione ENTER para fechar...")
        driver.quit()

if __name__ == "__main__":
    analyze_download_icons()
