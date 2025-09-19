#!/usr/bin/env python3
"""
Mastercard PDF Bot - Remoção Inteligente de Overlays
"""
import os
import time
import random
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
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class MastercardSmartBot:
    def __init__(self):
        self.download_dir = Path("mastercard_pdfs")
        self.download_dir.mkdir(exist_ok=True)
        
        options = Options()
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
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
        
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 45)
        self.actions = ActionChains(self.driver)
        
        logger.info("✅ Chrome iniciado (modo smart overlay)")
    
    def human_delay(self, min_sec=1, max_sec=3):
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def remove_specific_overlays(self):
        """Remove apenas overlays específicos que interceptam"""
        logger.info("🎯 Removendo overlays específicos...")
        
        # Só remove overlays que sabemos que interceptam, mas não os campos
        specific_overlays = [
            # Loading overlays
            ".loading-overlay",
            ".spinner", 
            ".loader",
            # Modal backdrops
            ".modal-backdrop",
            # Elementos com z-index muito alto (mas não inputs)
            "div[style*='z-index: 999']",
            "div[style*='z-index: 9999']"
        ]
        
        for selector in specific_overlays:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    # Verifica se não é um input antes de remover
                    tag_name = elem.tag_name.lower()
                    if tag_name not in ['input', 'button', 'select', 'textarea']:
                        self.driver.execute_script("arguments[0].style.display = 'none';", elem)
                        logger.info(f"🎯 Removido overlay: {selector}")
            except Exception as e:
                logger.debug(f"Não conseguiu remover {selector}: {e}")
    
    def make_element_clickable(self, element):
        """Torna elemento clicável removendo apenas sobreposições diretas"""
        logger.info("🔧 Tornando elemento clicável...")
        
        try:
            # Move elementos sobrepostos apenas na área do input
            script = """
            var element = arguments[0];
            var rect = element.getBoundingClientRect();
            
            // Remove apenas overlays que estão EXATAMENTE sobre o elemento
            var elementsAtPoint = document.elementsFromPoint(rect.left + rect.width/2, rect.top + rect.height/2);
            
            for (var i = 1; i < elementsAtPoint.length; i++) {
                var overlay = elementsAtPoint[i];
                if (overlay !== element && overlay.tagName !== 'INPUT' && overlay.tagName !== 'BUTTON') {
                    overlay.style.pointerEvents = 'none';
                    console.log('Overlay removido:', overlay);
                }
            }
            """
            
            self.driver.execute_script(script, element)
            logger.info("✅ Overlays sobre elemento removidos")
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao tornar clicável: {e}")
    
    def safe_fill_field(self, element, value, field_name):
        """Preenchimento seguro de campo"""
        logger.info(f"📝 Preenchendo campo {field_name}...")
        
        try:
            # Scroll para elemento
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.human_delay(1, 2)
            
            # Torna clicável
            self.make_element_clickable(element)
            
            # Método 1: Focus + clear + send_keys
            try:
                element.click()  # Tenta click normal primeiro
                self.human_delay(0.5, 1)
                element.clear()
                element.send_keys(value)
                
                # Verifica se foi preenchido
                current_value = element.get_attribute('value')
                if current_value == value:
                    logger.info(f"✅ {field_name} preenchido (método normal)")
                    return True
                    
            except Exception as e:
                logger.warning(f"⚠️ Método normal falhou para {field_name}: {e}")
            
            # Método 2: JavaScript click + send_keys
            try:
                self.driver.execute_script("arguments[0].click();", element)
                self.human_delay(0.5, 1)
                element.clear()
                element.send_keys(value)
                
                current_value = element.get_attribute('value')
                if current_value == value:
                    logger.info(f"✅ {field_name} preenchido (método JS click)")
                    return True
                    
            except Exception as e:
                logger.warning(f"⚠️ Método JS click falhou para {field_name}: {e}")
            
            # Método 3: JavaScript value direto
            try:
                self.driver.execute_script("""
                    arguments[0].value = arguments[1];
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                """, element, value)
                
                current_value = element.get_attribute('value')
                if current_value == value:
                    logger.info(f"✅ {field_name} preenchido (método JS value)")
                    return True
                    
            except Exception as e:
                logger.warning(f"⚠️ Método JS value falhou para {field_name}: {e}")
            
            logger.error(f"❌ Não conseguiu preencher {field_name}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro geral ao preencher {field_name}: {e}")
            return False
    
    def safe_click_button(self, button, button_name):
        """Clique seguro em botão"""
        logger.info(f"🖱️ Clicando botão {button_name}...")
        
        try:
            # Scroll para botão
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            self.human_delay(1, 2)
            
            # Torna clicável
            self.make_element_clickable(button)
            
            # Método 1: Click normal
            try:
                button.click()
                logger.info(f"✅ {button_name} clicado (método normal)")
                return True
            except:
                pass
            
            # Método 2: JavaScript click
            try:
                self.driver.execute_script("arguments[0].click();", button)
                logger.info(f"✅ {button_name} clicado (método JS)")
                return True
            except:
                pass
            
            # Método 3: ActionChains
            try:
                self.actions.move_to_element(button).click().perform()
                logger.info(f"✅ {button_name} clicado (método Actions)")
                return True
            except:
                pass
            
            logger.error(f"❌ Não conseguiu clicar {button_name}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao clicar {button_name}: {e}")
            return False
    
    def close_cookies(self):
        """Fecha cookies"""
        logger.info("🍪 Fechando cookies...")
        
        try:
            self.human_delay(2, 4)
            
            cookie_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            
            self.safe_click_button(cookie_btn, "cookies")
            self.human_delay(2, 3)
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao fechar cookies: {e}")
            return False
    
    def login_smart(self, username, password):
        """Login inteligente"""
        logger.info("🧠 Login inteligente...")
        
        try:
            # Acessa página
            logger.info("🌐 Acessando página...")
            self.driver.get("https://trc-techresource.mastercard.com")
            self.human_delay(5, 8)
            
            current_url = self.driver.current_url
            logger.info(f"📍 URL: {current_url}")
            
            # Fecha cookies
            self.close_cookies()
            
            # Aguarda e remove overlays específicos
            self.human_delay(3, 5)
            self.remove_specific_overlays()
            
            # Procura campos
            logger.info("🔍 Procurando campos...")
            
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "userId"))
            )
            logger.info("✅ Campo username encontrado")
            
            password_field = self.driver.find_element(By.NAME, "password")
            logger.info("✅ Campo password encontrado")
            
            # Preenche campos
            if not self.safe_fill_field(username_field, username, "username"):
                return False
            
            self.human_delay(1, 2)
            
            if not self.safe_fill_field(password_field, password, "password"):
                return False
            
            self.human_delay(2, 3)
            
            # Procura e clica botão
            logger.info("🔍 Procurando botão de login...")
            
            try:
                login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Iniciar')]")
                
                if not self.safe_click_button(login_btn, "login"):
                    # Fallback: Enter
                    logger.info("🔄 Fallback: Enter")
                    password_field.send_keys(Keys.RETURN)
                    
            except Exception as e:
                logger.warning(f"⚠️ Botão não encontrado: {e}")
                # Fallback: Enter
                password_field.send_keys(Keys.RETURN)
                logger.info("🔄 Fallback: Enter")
            
            # Monitora resultado
            logger.info("⏳ Monitorando resultado...")
            
            for i in range(30):
                time.sleep(1)
                current_url = self.driver.current_url
                
                if i % 5 == 0:
                    logger.info(f"  {i}s - URL: {current_url}")
                
                if "sign-in" not in current_url.lower():
                    logger.info(f"✅ Login realizado após {i}s!")
                    return True
                    
                # Verifica MFA
                page_source = self.driver.page_source.lower()
                if any(word in page_source for word in ["two", "factor", "verify", "code"]):
                    logger.info(f"🔑 MFA detectado após {i}s!")
                    time.sleep(15)
                    
                    if "sign-in" not in self.driver.current_url.lower():
                        logger.info("✅ MFA resolvido!")
                        return True
            
            logger.warning("⚠️ Timeout no login")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro no login: {e}")
            return False
    
    def close(self):
        try:
            self.driver.quit()
            logger.info("🔒 Navegador fechado")
        except:
            pass

def main():
    logger.info("🚀 Mastercard Bot - Overlay Inteligente")
    
    username = os.getenv('MASTERCARD_USER')
    password = os.getenv('MASTERCARD_PASS')
    
    if not username or not password:
        logger.error("❌ Configure credenciais no .env")
        return
    
    logger.info(f"🔑 Usando: {username}")
    
    bot = MastercardSmartBot()
    
    try:
        success = bot.login_smart(username, password)
        
        if success:
            logger.info("🎉 LOGIN REALIZADO COM SUCESSO!")
            input("Pressione Enter para fechar...")
        else:
            logger.error("❌ Login falhou")
    
    except KeyboardInterrupt:
        logger.info("⏹️ Interrompido")
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()
