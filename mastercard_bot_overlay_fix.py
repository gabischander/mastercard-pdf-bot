#!/usr/bin/env python3
"""
Mastercard PDF Bot - Corrigindo Overlays/Sobreposições
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

class MastercardOverlayBot:
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
        
        logger.info("✅ Chrome iniciado (modo overlay-fix)")
    
    def human_delay(self, min_sec=1, max_sec=3):
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def remove_overlays(self):
        """Remove overlays que podem estar interceptando cliques"""
        logger.info("🎭 Removendo overlays...")
        
        overlays_to_remove = [
            # Possíveis overlays
            "div[data-testid='grid-el']",
            ".c--hwsxdu",
            ".c--14phjq7", 
            ".c--10tw6or",
            ".iovFyl",
            ".ixugoz",
            ".kPERSC",
            # Outros overlays comuns
            ".modal-backdrop",
            ".overlay",
            ".loading-overlay",
            "[style*='z-index']",
            ".spinner",
            ".loader"
        ]
        
        for selector in overlays_to_remove:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    self.driver.execute_script("""
                        arguments[0].style.display = 'none';
                        arguments[0].style.visibility = 'hidden';
                        arguments[0].style.opacity = '0';
                        arguments[0].remove();
                    """, elem)
                    logger.info(f"🎭 Removido overlay: {selector}")
            except Exception as e:
                logger.debug(f"Não conseguiu remover {selector}: {e}")
    
    def wait_for_page_stable(self):
        """Aguarda página estabilizar (JS, CSS, etc)"""
        logger.info("⏳ Aguardando página estabilizar...")
        
        # Aguarda jQuery se existir
        try:
            self.wait.until(lambda driver: driver.execute_script("return jQuery.active == 0"))
            logger.info("✅ jQuery estável")
        except:
            logger.debug("jQuery não encontrado")
        
        # Aguarda document.readyState
        self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        logger.info("✅ Document pronto")
        
        # Aguarda possíveis animações CSS
        self.human_delay(3, 5)
    
    def safe_click(self, element, method="js"):
        """Clique seguro que tenta múltiplos métodos"""
        logger.info(f"🖱️ Clique seguro (método: {method})")
        
        try:
            if method == "js":
                # JavaScript click (bypassa overlays)
                self.driver.execute_script("arguments[0].click();", element)
                logger.info("✅ JS click realizado")
                return True
                
            elif method == "actions":
                # ActionChains (simula movimento mouse)
                self.actions.move_to_element(element).click().perform()
                logger.info("✅ ActionChains click realizado")
                return True
                
            elif method == "direct":
                # Click direto
                element.click()
                logger.info("✅ Click direto realizado")
                return True
                
        except Exception as e:
            logger.warning(f"⚠️ Erro no click {method}: {e}")
            return False
    
    def safe_send_keys(self, element, text):
        """Envio de teclas seguro"""
        logger.info("⌨️ Enviando teclas seguro...")
        
        try:
            # Limpa campo primeiro
            element.clear()
            self.human_delay(0.5, 1)
            
            # Foca no elemento
            self.driver.execute_script("arguments[0].focus();", element)
            self.human_delay(0.5, 1)
            
            # Envia texto
            element.send_keys(text)
            logger.info(f"✅ Texto enviado: {text}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao enviar teclas: {e}")
            return False
    
    def close_cookies(self):
        """Fecha cookies"""
        logger.info("🍪 Fechando cookies...")
        
        try:
            self.human_delay(2, 4)
            
            cookie_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            
            self.safe_click(cookie_btn, "js")
            logger.info("✅ Cookies fechados")
            self.human_delay(2, 3)
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao fechar cookies: {e}")
            return False
    
    def login_with_overlay_fix(self, username, password):
        """Login com correção de overlays"""
        logger.info("🔐 Login com correção de overlays...")
        
        try:
            # Acessa página
            logger.info("🌐 Acessando página...")
            self.driver.get("https://trc-techresource.mastercard.com")
            
            # Aguarda carregamento
            self.wait_for_page_stable()
            
            current_url = self.driver.current_url
            logger.info(f"📍 URL atual: {current_url}")
            
            # Fecha cookies
            self.close_cookies()
            
            # Aguarda estabilização
            self.wait_for_page_stable()
            
            # Remove overlays
            self.remove_overlays()
            
            # Procura campos
            logger.info("🔍 Procurando campos de login...")
            
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "userId"))
            )
            logger.info("✅ Campo username encontrado")
            
            password_field = self.driver.find_element(By.NAME, "password")
            logger.info("✅ Campo password encontrado")
            
            # Remove overlays novamente (podem ter aparecido)
            self.remove_overlays()
            
            # Tenta preencher campos com múltiplos métodos
            logger.info("📝 Preenchendo username...")
            
            # Scroll para o campo
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", username_field)
            self.human_delay(1, 2)
            
            # Remove overlays uma vez mais
            self.remove_overlays()
            
            # Tenta múltiplos métodos de preenchimento
            success = False
            
            # Método 1: Foco + send_keys
            try:
                self.driver.execute_script("arguments[0].focus();", username_field)
                self.human_delay(0.5, 1)
                self.safe_send_keys(username_field, username)
                success = True
                logger.info("✅ Username preenchido (método 1)")
            except:
                logger.warning("⚠️ Método 1 falhou")
            
            # Método 2: JS value set
            if not success:
                try:
                    self.driver.execute_script("arguments[0].value = arguments[1];", username_field, username)
                    self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", username_field)
                    success = True
                    logger.info("✅ Username preenchido (método 2 - JS)")
                except:
                    logger.warning("⚠️ Método 2 falhou")
            
            if not success:
                logger.error("❌ Não conseguiu preencher username")
                return False
            
            # Mesmo processo para password
            logger.info("📝 Preenchendo password...")
            
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", password_field)
            self.human_delay(1, 2)
            self.remove_overlays()
            
            success = False
            
            # Método 1: Foco + send_keys
            try:
                self.driver.execute_script("arguments[0].focus();", password_field)
                self.human_delay(0.5, 1)
                self.safe_send_keys(password_field, password)
                success = True
                logger.info("✅ Password preenchido (método 1)")
            except:
                logger.warning("⚠️ Método 1 falhou para password")
            
            # Método 2: JS value set
            if not success:
                try:
                    self.driver.execute_script("arguments[0].value = arguments[1];", password_field, password)
                    self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", password_field)
                    success = True
                    logger.info("✅ Password preenchido (método 2 - JS)")
                except:
                    logger.warning("⚠️ Método 2 falhou para password")
            
            if not success:
                logger.error("❌ Não conseguiu preencher password")
                return False
            
            # Aguarda e remove overlays antes de submeter
            self.human_delay(2, 3)
            self.remove_overlays()
            
            # Procura e clica botão de login
            logger.info("🔍 Procurando botão de login...")
            
            try:
                login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Iniciar')]")
                
                # Scroll para botão
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", login_btn)
                self.human_delay(1, 2)
                
                # Remove overlays
                self.remove_overlays()
                
                # Tenta clique múltiplos métodos
                if not self.safe_click(login_btn, "js"):
                    if not self.safe_click(login_btn, "actions"):
                        if not self.safe_click(login_btn, "direct"):
                            # Fallback: Enter no password
                            password_field.send_keys(Keys.RETURN)
                            logger.info("✅ Fallback: Enter enviado")
                
            except Exception as e:
                logger.warning(f"⚠️ Erro com botão: {e}")
                # Fallback: Enter
                password_field.send_keys(Keys.RETURN)
                logger.info("✅ Fallback: Enter enviado")
            
            # Aguarda resposta
            logger.info("⏳ Aguardando resposta...")
            
            for i in range(30):
                time.sleep(1)
                current_url = self.driver.current_url
                
                if i % 5 == 0:
                    logger.info(f"  {i}s - URL: {current_url}")
                
                if "sign-in" not in current_url.lower():
                    logger.info(f"✅ Login realizado com sucesso após {i}s!")
                    return True
                
                # Verifica MFA
                page_source = self.driver.page_source.lower()
                if any(word in page_source for word in ["two", "factor", "verify", "code"]):
                    logger.info(f"🔑 MFA detectado após {i}s!")
                    time.sleep(15)
                    
                    if "sign-in" not in self.driver.current_url.lower():
                        logger.info("✅ MFA resolvido!")
                        return True
            
            logger.warning("⚠️ Timeout - login não confirmado")
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
    logger.info("🚀 Mastercard Bot - Correção de Overlays")
    
    username = os.getenv('MASTERCARD_USER')
    password = os.getenv('MASTERCARD_PASS')
    
    if not username or not password:
        logger.error("❌ Configure credenciais no .env")
        return
    
    logger.info(f"🔑 Usando: {username}")
    
    bot = MastercardOverlayBot()
    
    try:
        success = bot.login_with_overlay_fix(username, password)
        
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
