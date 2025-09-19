#!/usr/bin/env python3
"""
Debug específico para analisar como "Publication Date" aparece na página
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def debug_publication_date():
    print("🔍 DEBUG: PUBLICATION DATE")
    print("=" * 50)
    
    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get("https://mastercardconnect.com")
        time.sleep(3)
        
        print("🎯 Navegue até a página de Announcements...")
        input("Pressione ENTER quando estiver vendo os documentos...")
        
        # Troca para aba mais recente
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            
        time.sleep(5)
        
        print("\n🔍 PROCURANDO POR DIFERENTES VARIAÇÕES DE 'PUBLICATION DATE':")
        
        # Variações de "Publication Date"
        pub_date_variations = [
            "Publication Date:",
            "Publication Date",
            "Published:",
            "Published",
            "Date:",
            "Date",
            "Pub Date:",
            "Pub Date"
        ]
        
        for variation in pub_date_variations:
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{variation}')]")
            print(f"   '{variation}': {len(elements)} elementos")
            
            if elements:
                for i, elem in enumerate(elements[:3]):
                    print(f"      {i+1}. {elem.text.strip()[:100]}")
                    
        print("\n🔍 PROCURANDO POR DATAS ESPECÍFICAS (Jul, Jun):")
        
        # Procura por meses específicos
        month_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Jul') or contains(text(), 'Jun')]")
        print(f"   Elementos com Jul/Jun: {len(month_elements)}")
        
        for i, elem in enumerate(month_elements[:10]):
            text = elem.text.strip()
            if text:
                print(f"      {i+1}. {text[:80]}")
                
        print("\n🔍 PROCURANDO POR DATAS DO FORMATO '1 Jul 2025':")
        
        # Procura por datas específicas
        date_patterns = ['1 Jul 2025', '30 Jun 2025', '01 Jul 2025', 'Jul 2025', 'Jun 2025']
        
        for pattern in date_patterns:
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{pattern}')]")
            print(f"   '{pattern}': {len(elements)} elementos")
            
            if elements:
                for i, elem in enumerate(elements[:2]):
                    print(f"      {i+1}. Tag: {elem.tag_name} | Texto: {elem.text.strip()[:60]}")
                    
        print("\n🔍 ANÁLISE COMPLETA DA PÁGINA:")
        
        # Pega todo o texto da página
        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Procura por linhas que contêm "Publication" ou datas
        lines = body_text.split('\n')
        relevant_lines = []
        
        for line in lines:
            if any(keyword in line for keyword in ['Publication', 'Jul', 'Jun', '2025']):
                relevant_lines.append(line.strip())
                
        print(f"   Linhas relevantes encontradas: {len(relevant_lines)}")
        
        for i, line in enumerate(relevant_lines[:15]):
            if line:
                print(f"      {i+1}. {line[:80]}")
                
        print("\n🔍 PROCURANDO ESTRUTURA DE CARDS/CONTAINERS:")
        
        # Procura por containers que podem ser documentos
        container_selectors = [
            "div",
            "[class*='card']",
            "[class*='item']", 
            "[class*='result']",
            "[class*='document']",
            "[class*='announcement']"
        ]
        
        for selector in container_selectors:
            containers = driver.find_elements(By.CSS_SELECTOR, selector)
            
            # Filtra containers que têm conteúdo relevante
            relevant_containers = []
            for container in containers:
                text = container.text
                if len(text) > 50 and any(keyword in text for keyword in ['Jul', 'Jun', 'Publication', 'GLB', 'LAC']):
                    relevant_containers.append(container)
                    
            if relevant_containers:
                print(f"   {selector}: {len(relevant_containers)} containers relevantes")
                
                for i, container in enumerate(relevant_containers[:3]):
                    lines = container.text.strip().split('\n')
                    first_line = lines[0] if lines else 'sem texto'
                    print(f"      {i+1}. {first_line[:60]}...")
                    
        print("\n🔍 ANÁLISE DE ELEMENTOS CLICÁVEIS:")
        
        # Procura por elementos clicáveis
        clickable_elements = driver.find_elements(By.XPATH, "//a | //button | //*[@onclick]")
        print(f"   Elementos clicáveis total: {len(clickable_elements)}")
        
        # Filtra os que parecem ser downloads
        download_elements = []
        for elem in clickable_elements:
            href = elem.get_attribute('href') or ''
            onclick = elem.get_attribute('onclick') or ''
            title = elem.get_attribute('title') or ''
            classes = elem.get_attribute('class') or ''
            
            if any(keyword in (href + onclick + title + classes).lower() 
                   for keyword in ['download', 'zip', 'pdf', 'export', 'file']):
                download_elements.append(elem)
                
        print(f"   Elementos com características de download: {len(download_elements)}")
        
        for i, elem in enumerate(download_elements[:5]):
            print(f"      {i+1}. <{elem.tag_name}> classes: {elem.get_attribute('class')[:40]}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        
    finally:
        input("\nPressione ENTER para fechar...")
        driver.quit()

if __name__ == "__main__":
    debug_publication_date()
