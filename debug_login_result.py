#!/usr/bin/env python3
"""
Debug do resultado do login
"""
import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

def debug_login():
    options = Options()
    options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    try:
        print("🔐 Fazendo login para debug...")
        
        # Acessa e faz login básico
        driver.get("https://trc-techresource.mastercard.com")
        time.sleep(5)
        
        # Fecha cookies
        try:
            cookie_btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            driver.execute_script("arguments[0].click();", cookie_btn)
            time.sleep(2)
        except:
            pass
        
        # Preenche campos
        username = os.getenv('MASTERCARD_USER')
        password = os.getenv('MASTERCARD_PASS')
        
        user_field = driver.find_element(By.NAME, "userId")
        pass_field = driver.find_element(By.NAME, "password")
        
        user_field.send_keys(username)
        pass_field.send_keys(password)
        time.sleep(1)
        
        # Clica login
        login_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Iniciar')]")
        driver.execute_script("arguments[0].click();", login_btn)
        
        # Aguarda e analisa resultado
        time.sleep(8)
        
        print(f"📍 URL final: {driver.current_url}")
        print(f"📄 Título: {driver.title}")
        
        # Procura por mensagens de erro
        error_selectors = [
            ".error",
            ".alert",
            ".message",
            "[class*='error']",
            "[class*='alert']",
            "[class*='invalid']",
            "[id*='error']",
            "[role='alert']"
        ]
        
        print("\n🔍 Procurando mensagens de erro...")
        for selector in error_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed() and elem.text.strip():
                        print(f"⚠️ Possível erro: {elem.text.strip()}")
            except:
                continue
        
        # Verifica se há textos com "invalid", "error", etc.
        page_text = driver.page_source.lower()
        error_keywords = ["invalid", "incorrect", "error", "failed", "denied"]
        
        print("\n🔍 Procurando palavras-chave de erro...")
        for keyword in error_keywords:
            if keyword in page_text:
                print(f"⚠️ Palavra-chave encontrada: '{keyword}'")
        
        # Lista elementos visíveis na página
        print("\n🔍 Elementos visíveis após login:")
        visible_elements = driver.find_elements(By.XPATH, "//*[text()]")
        for elem in visible_elements[:10]:  # Primeiros 10
            try:
                text = elem.text.strip()
                if text and len(text) < 100:
                    print(f"  📝 {text}")
            except:
                continue
        
        print("\n📸 Screenshot salva como debug_final.png")
        driver.save_screenshot("debug_final.png")
        
        input("Pressione Enter para fechar...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_login()
