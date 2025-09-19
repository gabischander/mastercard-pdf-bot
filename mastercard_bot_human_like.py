#!/usr/bin/env python3
"""
Mastercard PDF Bot - Simulando Comportamento Humano
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
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class MastercardHumanBot:
    def __init__(self):
        self.download_dir = Path("mastercard_pdfs")
        self.download_dir.mkdir(exist_ok=True)
        
        options = Options()
        
        # User-agent real (Mac Safari)
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15")
        
        # Configurações para parecer mais humano
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Download settings
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
        
        # Remove automation flags
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        })
        
        self.wait = WebDriverWait(self.driver, 45)  # Timeout maior
        logger.info("✅ Chrome iniciado (modo humano)")
    
    def human_delay(self, min_sec=1, max_sec=3):
        """Delay humano aleatório"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def human_type(self, element, text):
        """Digita como humano (com delays)"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # 50-150ms entre caracteres
    
    def screenshot(self, name="debug"):
        """Screenshot com timestamp"""
        try:
            path = f"{name}_{int(time.time())}.png"
            self.driver.save_screenshot(path)
            logger.info(f"📸 {path}")
        except Exception as e:
            logger.warning(f"Erro screenshot: {e}")
    
    def close_cookies(self):
        """Fecha cookies de forma humana"""
        logger.info("🍪 Fechando cookies...")
        
        try:
            self.human_delay(2, 4)  # Simula leitura
            
            cookie_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            
            # Move mouse para o botão (simula hover)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", cookie_btn)
            self.human_delay(0.5, 1)
            
            # Clica
            self.driver.execute_script("arguments[0].click();", cookie_btn)
            logger.info("✅ Cookies aceitos")
            
            self.human_delay(2, 3)
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao fechar cookies: {e}")
            return False
    
    def login_human_style(self, username, password):
        """Login simulando comportamento humano"""
        logger.info("�� Login estilo humano...")
        
        try:
            # Acessa página
            logger.info("📱 Acessando página...")
            self.driver.get("https://trc-techresource.mastercard.com")
            
            # Aguarda carregamento (como humano faria)
            self.human_delay(5, 8)
            
            current_url = self.driver.current_url
            logger.info(f"📍 URL: {current_url}")
            
            # Screenshot inicial
            self.screenshot("page_loaded")
            
            # Fecha cookies
            self.close_cookies()
            
            # Aguarda página estabilizar
            logger.info("⏳ Aguardando página estabilizar...")
            self.human_delay(3, 5)
            
            # Procura campos de login
            logger.info("🔍 Procurando campos de login...")
            
            try:
                username_field = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "userId"))
                )
                logger.info("✅ Campo username encontrado")
            except:
                logger.error("❌ Campo username não encontrado")
                return False
            
            try:
                password_field = self.driver.find_element(By.NAME, "password")
                logger.info("✅ Campo password encontrado")
            except:
                logger.error("❌ Campo password não encontrado")
                return False
            
            # Simula foco no campo (como 1Password faria)
            logger.info("📝 Preenchendo como humano...")
            
            # Clica no campo username primeiro
            username_field.click()
            self.human_delay(0.5, 1)
            
            # Digita username devagar
            self.human_type(username_field, username)
            logger.info(f"✅ Username digitado: {username}")
            
            self.human_delay(1, 2)  # Pausa entre campos
            
            # Clica no campo password
            password_field.click()
            self.human_delay(0.5, 1)
            
            # Digita password devagar
            self.human_type(password_field, password)
            logger.info("✅ Password digitada")
            
            self.human_delay(1, 2)  # Pausa antes de submeter
            self.screenshot("credentials_filled")
            
            # Procura botão de login
            logger.info("🔍 Procurando botão de login...")
            
            try:
                login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Iniciar')]")
                
                # Scroll para o botão se necessário
                self.driver.execute_script("arguments[0].scrollIntoView(true);", login_btn)
                self.human_delay(0.5, 1)
                
                # Clica no botão
                self.driver.execute_script("arguments[0].click();", login_btn)
                logger.info("✅ Botão de login clicado")
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao clicar botão: {e}")
                # Fallback: Enter
                password_field.send_keys(Keys.RETURN)
                logger.info("✅ Enter enviado como fallback")
            
            # AGUARDA MAIS TEMPO (possível MFA)
            logger.info("⏳ Aguardando resposta (possível MFA)...")
            
            for i in range(30):  # 30 segundos de monitoramento
                time.sleep(1)
                current_url = self.driver.current_url
                page_title = self.driver.title
                
                # Verifica mudanças a cada 5 segundos
                if i % 5 == 0:
                    logger.info(f"  {i}s - URL: {current_url}")
                    logger.info(f"  {i}s - Title: {page_title}")
                
                # Verifica se saiu da página de login
                if "sign-in" not in current_url.lower():
                    logger.info(f"✅ URL mudou após {i}s! Possível sucesso")
                    self.screenshot("login_success")
                    return True
                
                # Verifica se apareceu algo sobre MFA/2FA
                page_source = self.driver.page_source.lower()
                mfa_keywords = ["two", "factor", "authentication", "verify", "code", "sms", "email"]
                
                if any(keyword in page_source for keyword in mfa_keywords):
                    logger.info(f"🔑 Possível MFA detectado após {i}s!")
                    self.screenshot(f"mfa_detected_{i}s")
                    
                    # Aguarda mais tempo para MFA
                    logger.info("⏳ Aguardando MFA ser resolvido...")
                    time.sleep(15)
                    
                    final_url = self.driver.current_url
                    if "sign-in" not in final_url.lower():
                        logger.info("✅ MFA resolvido com sucesso!")
                        return True
                    else:
                        logger.warning("⚠️ MFA não foi resolvido")
                        return False
            
            # Se chegou aqui, não mudou a URL
            logger.warning("⚠️ URL não mudou após 30s")
            self.screenshot("login_timeout")
            
            # Verifica se há mensagens de erro
            self.check_for_errors()
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro no login: {e}")
            self.screenshot("login_exception")
            return False
    
    def check_for_errors(self):
        """Verifica mensagens de erro"""
        logger.info("🔍 Verificando erros...")
        
        # Procura elementos com texto de erro
        all_elements = self.driver.find_elements(By.XPATH, "//*[text()]")
        
        error_words = ["invalid", "incorrect", "wrong", "failed", "error", "denied"]
        
        for elem in all_elements:
            try:
                text = elem.text.strip().lower()
                if text and any(word in text for word in error_words):
                    logger.warning(f"⚠️ Possível erro: {elem.text.strip()}")
            except:
                continue
    
    def close(self):
        """Fecha navegador"""
        try:
            self.driver.quit()
            logger.info("🔒 Navegador fechado")
        except:
            pass

def main():
    logger.info("🚀 Mastercard Bot - Modo Humano")
    
    # Credenciais
    username = os.getenv('MASTERCARD_USER')
    password = os.getenv('MASTERCARD_PASS')
    
    if not username or not password:
        logger.error("❌ Configure credenciais no .env")
        return
    
    logger.info(f"🔑 Usando: {username}")
    
    # Executa bot
    bot = MastercardHumanBot()
    
    try:
        success = bot.login_human_style(username, password)
        
        if success:
            logger.info("🎉 LOGIN REALIZADO COM SUCESSO!")
            logger.info("🧭 Próximo passo: navegar e coletar PDFs")
            
            # Deixa navegador aberto para exploração manual
            input("Pressione Enter para fechar (explore manualmente se quiser)...")
        else:
            logger.error("❌ Login falhou - verifique credenciais ou MFA")
    
    except KeyboardInterrupt:
        logger.info("⏹️ Interrompido")
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()
