#!/usr/bin/env python3
"""
Debug robusto que aguarda elementos
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

def debug_robust():
    options = Options()
    options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    wait = WebDriverWait(driver, 30)
    
    try:
        print("🔐 Debug robusto do login...")
        
        # Acessa página
        driver.get("https://trc-techresource.mastercard.com")
        time.sleep(7)  # Aguarda mais tempo
        
        print(f"📍 URL após carregamento: {driver.current_url}")
        
        # Aguarda aparecer algum input
        print("⏳ Aguardando inputs aparecerem...")
        try:
            wait.until(lambda d: len(d.find_elements(By.TAG_NAME, "input")) > 5)
            print("✅ Inputs detectados")
        except:
            print("⚠️ Timeout aguardando inputs")
        
        # Lista todos inputs
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"📝 Total de inputs: {len(inputs)}")
        
        for i, inp in enumerate(inputs):
            try:
                inp_type = inp.get_attribute("type") or "text"
                inp_name = inp.get_attribute("name") or ""
                inp_id = inp.get_attribute("id") or ""
                print(f"  {i+1}. type='{inp_type}' name='{inp_name}' id='{inp_id}'")
            except:
                print(f"  {i+1}. [Erro ao ler]")
        
        # Tenta fechar cookies
        print("🍪 Tentando fechar cookies...")
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            driver.execute_script("arguments[0].click();", cookie_btn)
            print("✅ Cookies fechados")
            time.sleep(3)
        except:
            print("⚠️ Não foi possível fechar cookies")
        
        # Procura campos específicos
        username_field = None
        password_field = None
        
        # Tenta diferentes seletores
        user_selectors = [
            ("name", "userId"),
            ("id", "ConnectInput0-ref-id"),
            ("xpath", "//input[@placeholder*='utilizador']"),
            ("xpath", "//input[@placeholder*='ID']")
        ]
        
        for method, selector in user_selectors:
            try:
                if method == "xpath":
                    username_field = driver.find_element(By.XPATH, selector)
                else:
                    username_field = driver.find_element(getattr(By, method.upper()), selector)
                print(f"✅ Campo username encontrado via {method}='{selector}'")
                break
            except:
                continue
        
        # Mesmo para password
        pass_selectors = [
            ("name", "password"),
            ("id", "ConnectInput1-ref-id"),
            ("type", "password")
        ]
        
        for method, selector in pass_selectors:
            try:
                if method == "type":
                    password_field = driver.find_element(By.CSS_SELECTOR, f"input[type='{selector}']")
                else:
                    password_field = driver.find_element(getattr(By, method.upper()), selector)
                print(f"✅ Campo password encontrado via {method}='{selector}'")
                break
            except:
                continue
        
        if username_field and password_field:
            print("🎯 Ambos os campos encontrados!")
            
            # Preenche
            username = os.getenv('MASTERCARD_USER')
            password = os.getenv('MASTERCARD_PASS')
            
            username_field.send_keys(username)
            password_field.send_keys(password)
            print("📝 Credenciais preenchidas")
            
            # Procura botão
            buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"🔘 Encontrados {len(buttons)} botões")
            
            for i, btn in enumerate(buttons):
                try:
                    text = btn.text.strip()
                    if text:
                        print(f"  Botão {i+1}: '{text}'")
                except:
                    continue
            
            # Tenta clicar botão de login
            try:
                login_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Iniciar')]")
                driver.execute_script("arguments[0].click();", login_btn)
                print("✅ Botão de login clicado")
                
                # Aguarda resultado
                time.sleep(10)
                
                final_url = driver.current_url
                print(f"📍 URL final: {final_url}")
                
                if final_url != driver.current_url:
                    print("✅ URL mudou - possível sucesso")
                else:
                    print("⚠️ URL não mudou - possível erro")
                
                # Procura mensagens na página
                page_text = driver.page_source
                
                error_words = ["invalid", "incorrect", "error", "failed", "wrong"]
                success_words = ["welcome", "dashboard", "home", "portal"]
                
                print("\n🔍 Análise da página:")
                for word in error_words:
                    if word.lower() in page_text.lower():
                        print(f"❌ Palavra de erro encontrada: '{word}'")
                
                for word in success_words:
                    if word.lower() in page_text.lower():
                        print(f"✅ Palavra de sucesso encontrada: '{word}'")
                        
            except Exception as e:
                print(f"❌ Erro ao clicar botão: {e}")
        
        else:
            print("❌ Campos não encontrados")
            if not username_field:
                print("  - Campo username não encontrado")
            if not password_field:
                print("  - Campo password não encontrado")
        
        # Screenshot final
        driver.save_screenshot("debug_robust_final.png")
        print("📸 Screenshot: debug_robust_final.png")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_robust()
