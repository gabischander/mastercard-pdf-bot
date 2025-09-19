#!/usr/bin/env python3
"""
Encontra mensagem de erro específica
"""
import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

def find_error():
    options = Options()
    options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    wait = WebDriverWait(driver, 30)
    
    try:
        print("🔍 Procurando mensagem de erro específica...")
        
        # Processo de login
        driver.get("https://trc-techresource.mastercard.com")
        time.sleep(7)
        
        # Fecha cookies
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            driver.execute_script("arguments[0].click();", cookie_btn)
            time.sleep(2)
        except:
            pass
        
        # Preenche campos
        username_field = driver.find_element(By.NAME, "userId")
        password_field = driver.find_element(By.NAME, "password")
        
        username = os.getenv('MASTERCARD_USER')
        password = os.getenv('MASTERCARD_PASS')
        
        username_field.send_keys(username)
        password_field.send_keys(password)
        
        # Clica login
        login_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Iniciar')]")
        driver.execute_script("arguments[0].click();", login_btn)
        
        # Aguarda resposta
        time.sleep(8)
        
        print(f"📧 Tentando login com: {username}")
        print(f"📍 URL após tentativa: {driver.current_url}")
        
        # Procura mensagens de erro específicas
        error_selectors = [
            ".error-message",
            ".alert-danger", 
            ".validation-error",
            "[role='alert']",
            ".message",
            ".notification",
            "[class*='error']",
            "[class*='invalid']",
            "[class*='fail']"
        ]
        
        print("\n🚨 Mensagens de erro encontradas:")
        found_errors = False
        
        for selector in error_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed():
                        text = elem.text.strip()
                        if text and len(text) > 3:
                            print(f"  ❌ {text}")
                            found_errors = True
            except:
                continue
        
        if not found_errors:
            print("  (Nenhuma mensagem de erro específica encontrada)")
        
        # Procura por textos próximos aos campos de login
        print("\n🔍 Textos próximos aos campos de login:")
        
        try:
            # Elementos próximos ao campo username
            username_parent = username_field.find_element(By.XPATH, "./..")
            nearby_elements = username_parent.find_elements(By.XPATH, ".//*[text()]")
            
            for elem in nearby_elements:
                text = elem.text.strip()
                if text and len(text) > 3 and len(text) < 200:
                    if any(word in text.lower() for word in ["invalid", "incorrect", "error", "fail", "wrong"]):
                        print(f"  ⚠️ {text}")
        except:
            pass
        
        # Verifica se há algum indicador visual de erro
        print("\n🎨 Verificando indicadores visuais:")
        
        # Campos com classe de erro
        if "error" in username_field.get_attribute("class") or "":
            print("  ❌ Campo username tem classe de erro")
        if "error" in password_field.get_attribute("class") or "":
            print("  ❌ Campo password tem classe de erro")
        
        # Salva HTML para análise manual
        with open("error_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("\n💾 HTML da página salvo em: error_page.html")
        
        # Screenshot
        driver.save_screenshot("error_analysis.png")
        print("📸 Screenshot salva em: error_analysis.png")
        
        # Sugestões
        print("\n💡 Possíveis problemas:")
        print("  1. Credenciais incorretas")
        print("  2. Conta bloqueada/suspensa")
        print("  3. Necessário 2FA/MFA")
        print("  4. Captcha não resolvido")
        print("  5. Política de segurança (VPN, localização)")
        
        print(f"\n🔐 Verifique se as credenciais estão corretas:")
        print(f"  Username: {username}")
        print(f"  Password: {'*' * len(password) if password else 'NÃO CONFIGURADA'}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    find_error()
