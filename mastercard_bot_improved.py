#!/usr/bin/env python3
"""
Mastercard PDF Bot - Versão com melhor aguarda JS
"""
import os
import time
import logging
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class MastercardBotImproved:
    def __init__(self, headless=False):
        self.download_dir = Path("mastercard_pdfs")
        self.download_dir.mkdir(exist_ok=True)
        
        options = Options()
        if headless:
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Prefs para download
        prefs = {
            "download.default_directory": str(self.download_dir.absolute()),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True
        }
        options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 30)  # Timeout maior
        logger.info("✅ Chrome iniciado")
    
    def screenshot(self, name="debug"):
        """Salva screenshot"""
        try:
            path = f"{name}_{int(time.time())}.png"
            self.driver.save_screenshot(path)
            logger.info(f"📸 Screenshot: {path}")
        except Exception as e:
            logger.warning(f"Erro screenshot: {e}")
    
    def wait_for_js_load(self, max_wait=30):
        """Aguarda JavaScript carregar completamente"""
        logger.info("⏳ Aguardando JavaScript carregar...")
        
        for i in range(max_wait):
            try:
                # Verifica se página carregou
                ready_state = self.driver.execute_script("return document.readyState")
                
                # Verifica se há inputs na página
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                
                if ready_state == "complete" and len(inputs) > 0:
                    logger.info(f"✅ JS carregado após {i+1}s ({len(inputs)} inputs)")
                    return True
                    
                time.sleep(1)
            except:
                time.sleep(1)
                continue
        
        logger.warning("⚠️ JS pode não ter carregado completamente")
        return False
    
    def find_login_fields(self):
        """Encontra campos de login de forma robusta"""
        logger.info("🔍 Procurando campos de login...")
        
        # Aguarda JS carregar
        self.wait_for_js_load()
        
        # Screenshot para debug
        self.screenshot("finding_fields")
        
        # Lista todos inputs encontrados
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        logger.info(f"📝 Encontrados {len(inputs)} inputs")
        
        username_field = None
        password_field = None
        
        for i, input_field in enumerate(inputs):
            try:
                input_type = input_field.get_attribute("type") or "text"
                input_name = input_field.get_attribute("name") or ""
                input_id = input_field.get_attribute("id") or ""
                input_placeholder = input_field.get_attribute("placeholder") or ""
                
                logger.info(f"  Input {i+1}: type='{input_type}' name='{input_name}' id='{input_id}' placeholder='{input_placeholder}'")
                
                # Identifica campo de email/username
                if input_type in ["email", "text"] and not username_field:
                    if any(keyword in (input_name + input_id + input_placeholder).lower() 
                           for keyword in ["email", "user", "login", "name"]):
                        username_field = input_field
                        logger.info(f"✅ Campo username: Input {i+1}")
                
                # Identifica campo de password
                if input_type == "password" and not password_field:
                    password_field = input_field
                    logger.info(f"✅ Campo password: Input {i+1}")
                    
            except Exception as e:
                logger.debug(f"Erro ao ler input {i+1}: {e}")
        
        return username_field, password_field
    
    def login(self, username, password):
        """Login melhorado"""
        logger.info("🔐 Iniciando login...")
        
        try:
            # Acessa página
            self.driver.get("https://trc-techresource.mastercard.com")
            logger.info("📱 Página acessada")
            
            # Aguarda redirecionamento
            time.sleep(5)
            
            current_url = self.driver.current_url
            logger.info(f"📍 URL após redirecionamento: {current_url}")
            
            if "mastercardconnect.com" not in current_url:
                logger.error("❌ Não redirecionou para MastercardConnect")
                return False
            
            # Procura campos de login
            username_field, password_field = self.find_login_fields()
            
            if not username_field:
                logger.error("❌ Campo de username não encontrado")
                self.screenshot("no_username")
                return False
            
            if not password_field:
                logger.error("❌ Campo de password não encontrado") 
                self.screenshot("no_password")
                return False
            
            # Preenche credenciais
            logger.info("📝 Preenchendo credenciais...")
            
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(1)
            
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            self.screenshot("credentials_filled")
            
            # Procura botão de submit
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            submit_button = None
            
            for button in buttons:
                try:
                    button_text = button.text.strip().lower()
                    button_type = button.get_attribute("type") or ""
                    
                    if (button_type == "submit" or 
                        any(keyword in button_text for keyword in ["sign in", "login", "entrar", "submit"])):
                        submit_button = button
                        logger.info(f"✅ Botão encontrado: '{button.text}'")
                        break
                except:
                    continue
            
            if submit_button:
                submit_button.click()
                logger.info("🚀 Login enviado")
            else:
                logger.warning("⚠️ Botão não encontrado, usando Enter")
                password_field.send_keys(Keys.RETURN)
            
            # Aguarda resultado
            time.sleep(8)
            self.screenshot("after_login")
            
            new_url = self.driver.current_url
            logger.info(f"📍 Nova URL: {new_url}")
            
            # Verifica sucesso (mais flexível)
            if ("sign-in" not in new_url.lower() and 
                "login" not in new_url.lower()):
                logger.info("✅ Login realizado com sucesso!")
                return True
            else:
                logger.warning("⚠️ Login pode ter falhado")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no login: {e}")
            self.screenshot("login_exception")
            return False
    
    def test_navigation(self):
        """Testa navegação básica após login"""
        logger.info("🧭 Testando navegação...")
        
        try:
            # Tenta encontrar links/botões na página
            time.sleep(3)
            
            # Procura por links que podem levar a documentos
            links = self.driver.find_elements(By.TAG_NAME, "a")
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            
            logger.info(f"🔗 Encontrados {len(links)} links e {len(buttons)} botões")
            
            # Lista alguns links para debug
            for i, link in enumerate(links[:10]):
                try:
                    href = link.get_attribute("href") or ""
                    text = link.text.strip()
                    if text:
                        logger.info(f"  Link {i+1}: '{text}' -> {href}")
                except:
                    continue
            
            self.screenshot("navigation_test")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na navegação: {e}")
            return False
    
    def close(self):
        """Fecha navegador"""
        try:
            self.driver.quit()
            logger.info("🔒 Navegador fechado")
        except:
            pass

def main():
    logger.info("🚀 Mastercard PDF Bot - Versão Melhorada")
    
    # Credenciais
    username = os.getenv('MASTERCARD_USER')
    password = os.getenv('MASTERCARD_PASS')
    
    if not username or not password:
        logger.error("❌ Configure MASTERCARD_USER e MASTERCARD_PASS no .env")
        username = input("Email: ")
        password = input("Senha: ")
    
    # Executa bot
    bot = MastercardBotImproved(headless=False)
    
    try:
        if bot.login(username, password):
            bot.test_navigation()
        else:
            logger.error("❌ Login falhou")
    
    except KeyboardInterrupt:
        logger.info("⏹️ Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()
