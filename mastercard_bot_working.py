#!/usr/bin/env python3
"""
Mastercard PDF Bot - Versão Funcional
Corrige problema do modal de cookies
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

class MastercardBotWorking:
    def __init__(self, headless=False):
        self.download_dir = Path("mastercard_pdfs")
        self.download_dir.mkdir(exist_ok=True)
        
        options = Options()
        if headless:
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
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
        self.wait = WebDriverWait(self.driver, 30)
        logger.info("✅ Chrome iniciado")
    
    def screenshot(self, name="debug"):
        """Salva screenshot"""
        try:
            path = f"{name}_{int(time.time())}.png"
            self.driver.save_screenshot(path)
            logger.info(f"📸 Screenshot: {path}")
        except Exception as e:
            logger.warning(f"Erro screenshot: {e}")
    
    def close_cookie_modal(self):
        """Fecha modal de cookies"""
        logger.info("🍪 Fechando modal de cookies...")
        
        try:
            # Aguarda modal aparecer
            time.sleep(2)
            
            # Seletores para botões de aceitar cookies
            cookie_selectors = [
                # Botões OneTrust (mais comuns)
                "#onetrust-accept-btn-handler",
                ".onetrust-accept-btn-handler",
                "button[id*='accept']",
                "button[class*='accept']",
                # Textos específicos
                "//button[contains(text(), 'Accept All')]",
                "//button[contains(text(), 'Aceitar')]",
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'Allow All')]",
                # IDs/classes específicas do OneTrust
                ".ot-pc-refuse-all-handler",
                "#accept-recommended-btn-handler",
                ".save-preference-btn-handler"
            ]
            
            for selector in cookie_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # Usa JavaScript para clicar (evita interceptação)
                            self.driver.execute_script("arguments[0].click();", element)
                            logger.info(f"✅ Modal fechado via: {selector}")
                            time.sleep(2)
                            return True
                except Exception as e:
                    logger.debug(f"Tentativa com {selector} falhou: {e}")
                    continue
            
            # Se não funcionou, tenta fechar com ESC
            from selenium.webdriver.common.keys import Keys
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            logger.info("✅ Tentativa ESC para fechar modal")
            time.sleep(1)
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao fechar modal de cookies: {e}")
    
    def wait_for_js_load(self, max_wait=30):
        """Aguarda JavaScript carregar"""
        logger.info("⏳ Aguardando JavaScript...")
        
        for i in range(max_wait):
            try:
                ready_state = self.driver.execute_script("return document.readyState")
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                
                if ready_state == "complete" and len(inputs) > 0:
                    logger.info(f"✅ JS carregado ({len(inputs)} inputs)")
                    return True
                    
                time.sleep(1)
            except:
                time.sleep(1)
                continue
        
        return False
    
    def login(self, username, password):
        """Login com tratamento de modais"""
        logger.info("🔐 Iniciando login...")
        
        try:
            # Acessa página
            self.driver.get("https://trc-techresource.mastercard.com")
            logger.info("📱 Página acessada")
            
            # Aguarda redirecionamento
            time.sleep(5)
            
            current_url = self.driver.current_url
            logger.info(f"📍 URL: {current_url}")
            
            # Fecha modal de cookies ANTES de procurar campos
            self.close_cookie_modal()
            
            # Aguarda JS carregar
            self.wait_for_js_load()
            
            # Procura campos de login
            username_field = None
            password_field = None
            
            # Seletores específicos que descobrimos
            try:
                username_field = self.driver.find_element(By.NAME, "userId")
                logger.info("✅ Campo username encontrado por name='userId'")
            except:
                try:
                    username_field = self.driver.find_element(By.ID, "ConnectInput0-ref-id")
                    logger.info("✅ Campo username encontrado por ID")
                except:
                    logger.error("❌ Campo username não encontrado")
                    return False
            
            try:
                password_field = self.driver.find_element(By.NAME, "password")
                logger.info("✅ Campo password encontrado por name='password'")
            except:
                try:
                    password_field = self.driver.find_element(By.ID, "ConnectInput1-ref-id")
                    logger.info("✅ Campo password encontrado por ID")
                except:
                    logger.error("❌ Campo password não encontrado")
                    return False
            
            # Preenche credenciais
            logger.info("📝 Preenchendo credenciais...")
            
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(1)
            
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            self.screenshot("credentials_ready")
            
            # Fecha modal novamente (pode ter aparecido)
            self.close_cookie_modal()
            
            # Procura e clica botão de login de forma mais robusta
            login_buttons = [
                "//button[contains(text(), 'Sign In')]",
                "//button[contains(text(), 'Iniciar')]",
                "//button[contains(text(), 'Entrar')]",
                "//button[@type='submit']",
                "button[type='submit']"
            ]
            
            button_clicked = False
            for selector in login_buttons:
                try:
                    if selector.startswith("//"):
                        buttons = self.driver.find_elements(By.XPATH, selector)
                    else:
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            # Scroll para o botão
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                            time.sleep(1)
                            
                            # Clica usando JavaScript
                            self.driver.execute_script("arguments[0].click();", button)
                            logger.info(f"✅ Botão clicado: {button.text}")
                            button_clicked = True
                            break
                    
                    if button_clicked:
                        break
                        
                except Exception as e:
                    logger.debug(f"Erro com {selector}: {e}")
                    continue
            
            if not button_clicked:
                logger.warning("⚠️ Botão não encontrado, usando Enter")
                password_field.send_keys(Keys.RETURN)
            
            # Aguarda resultado
            time.sleep(8)
            self.screenshot("after_login")
            
            new_url = self.driver.current_url
            logger.info(f"📍 Nova URL: {new_url}")
            
            # Verifica sucesso
            if ("sign-in" not in new_url.lower() and 
                "login" not in new_url.lower()):
                logger.info("✅ Login realizado com sucesso!")
                return True
            else:
                logger.warning("⚠️ Login pode ter falhado")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no login: {e}")
            self.screenshot("login_error")
            return False
    
    def close(self):
        """Fecha navegador"""
        try:
            self.driver.quit()
            logger.info("🔒 Navegador fechado")
        except:
            pass

def main():
    logger.info("🚀 Mastercard PDF Bot - Versão Funcional")
    
    # Credenciais
    username = os.getenv('MASTERCARD_USER')
    password = os.getenv('MASTERCARD_PASS')
    
    if not username or not password:
        logger.error("❌ Configure MASTERCARD_USER e MASTERCARD_PASS no .env")
        username = input("Email: ")
        password = input("Senha: ")
    
    # Executa bot
    bot = MastercardBotWorking(headless=False)
    
    try:
        if bot.login(username, password):
            logger.info("🎉 Login funcionando! Próximo passo: implementar coleta de PDFs")
            input("Pressione Enter para continuar com exploração manual...")
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
