#!/usr/bin/env python3
"""
Captura HTML da página para análise manual
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def capture_html():
    print("🕷️ CAPTURA DE HTML DA PÁGINA")
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
            
        print("⏳ Aguardando carregamento...")
        time.sleep(8)
        
        # Captura HTML completo
        html = driver.page_source
        
        # Salva HTML em arquivo
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        print("✅ HTML salvo em 'page_source.html'")
        
        # Procura por padrões simples
        print("\n🔍 ANÁLISE RÁPIDA DO HTML:")
        
        # Conta elementos básicos
        body = driver.find_element(By.TAG_NAME, "body")
        all_links = driver.find_elements(By.TAG_NAME, "a")
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        
        print(f"   Links: {len(all_links)}")
        print(f"   Botões: {len(all_buttons)}")
        print(f"   Inputs: {len(all_inputs)}")
        
        # Procura por elementos que contêm 'Jun' ou 'Jul'
        date_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Jun') or contains(text(), 'Jul')]")
        print(f"   Elementos com Jun/Jul: {len(date_elements)}")
        
        # Lista alguns elementos com datas
        print("\n📅 ELEMENTOS COM DATAS:")
        for i, elem in enumerate(date_elements[:5]):
            text = elem.text.strip()[:80]
            tag = elem.tag_name
            classes = elem.get_attribute('class') or 'sem classes'
            print(f"   {i+1}. <{tag}> {text} | classes: {classes[:40]}")
            
        # Busca simples por padrões de download
        print("\n📥 BUSCA POR PADRÕES DE DOWNLOAD:")
        
        # Busca no HTML por palavras-chave
        html_lower = html.lower()
        download_patterns = ['download', 'zip', 'pdf', 'file', 'arrow-down', 'fa-download']
        
        for pattern in download_patterns:
            count = html_lower.count(pattern)
            if count > 0:
                print(f"   '{pattern}': {count} ocorrências")
                
        # Extrai trechos específicos com datas
        print("\n📄 TRECHOS COM DATAS (primeiros 3):")
        
        import re
        date_pattern = r'.*?(\d{1,2}\s+(?:Jun|Jul)\s+\d{4}).*?'
        matches = re.findall(date_pattern, html, re.IGNORECASE | re.DOTALL)
        
        for i, match in enumerate(matches[:3]):
            print(f"   {i+1}. {match}")
            
        # Busca por onclick e href suspeitos
        onclick_pattern = r'onclick="([^"]*)"'
        href_pattern = r'href="([^"]*)"'
        
        onclick_matches = re.findall(onclick_pattern, html, re.IGNORECASE)
        href_matches = re.findall(href_pattern, html, re.IGNORECASE)
        
        print(f"\n🖱️ EVENTOS ONCLICK: {len(onclick_matches)}")
        for onclick in onclick_matches[:5]:
            if 'download' in onclick.lower() or 'export' in onclick.lower():
                print(f"   {onclick[:60]}...")
                
        print(f"\n🔗 LINKS HREF: {len(href_matches)}")
        for href in href_matches[:10]:
            if any(keyword in href.lower() for keyword in ['download', 'zip', 'pdf', 'export']):
                print(f"   {href}")
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        
    finally:
        input("\nPressione ENTER para fechar...")
        driver.quit()

if __name__ == "__main__":
    capture_html()
