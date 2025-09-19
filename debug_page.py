#!/usr/bin/env python3
"""
Debug da página de login para encontrar os seletores corretos
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def debug_page():
    options = Options()
    options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    try:
        print("🔍 Acessando página...")
        driver.get("https://trc-techresource.mastercard.com")
        time.sleep(5)
        
        print(f"📍 URL: {driver.current_url}")
        print(f"📄 Título: {driver.title}")
        
        # Salva HTML da página
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("📄 HTML salvo em: page_source.html")
        
        # Procura todos os inputs
        print("\n🔍 Todos os inputs encontrados:")
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for i, inp in enumerate(inputs):
            try:
                inp_type = inp.get_attribute("type") or "text"
                inp_name = inp.get_attribute("name") or ""
                inp_id = inp.get_attribute("id") or ""
                inp_class = inp.get_attribute("class") or ""
                inp_placeholder = inp.get_attribute("placeholder") or ""
                
                print(f"  {i+1}. type='{inp_type}' name='{inp_name}' id='{inp_id}'")
                if inp_class:
                    print(f"      class='{inp_class}'")
                if inp_placeholder:
                    print(f"      placeholder='{inp_placeholder}'")
                print()
            except:
                print(f"  {i+1}. [Erro ao ler atributos]")
        
        # Procura todos os botões
        print("\n🔘 Todos os botões encontrados:")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for i, btn in enumerate(buttons):
            try:
                btn_type = btn.get_attribute("type") or ""
                btn_text = btn.text.strip()
                btn_class = btn.get_attribute("class") or ""
                
                print(f"  {i+1}. type='{btn_type}' text='{btn_text}'")
                if btn_class:
                    print(f"      class='{btn_class}'")
                print()
            except:
                print(f"  {i+1}. [Erro ao ler botão]")
        
        # Screenshot
        driver.save_screenshot("debug_full_page.png")
        print("📸 Screenshot: debug_full_page.png")
        
        input("Pressione Enter para fechar...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_page()
