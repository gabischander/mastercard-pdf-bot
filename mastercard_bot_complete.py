#!/usr/bin/env python3
"""
Mastercard PDF Bot - Versão Completa (Cookies + Idioma + MFA)
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
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class MastercardCompleteBot:
    def __init__(self):
        self.download_dir = Path("mastercard_pdfs")
        self.download_dir.mkdir(exist_ok=True)
        
        options = Options()
        # NAVEGADOR VISÍVEL (sem --headless)
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Janela grande para ver bem
        options.add_argument("--window-size=1400,1000")
        
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
        
        self.wait = WebDriverWait(self.driver, 45)
        logger.info("✅ Chrome VISÍVEL iniciado")
    
    def close_all_overlays(self):
        """Fecha TODOS os overlays: cookies, idioma, etc"""
        logger.info("🧹 Fechando TODOS os overlays...")
        
        # 1. Cookies (OneTrust)
        try:
            logger.info("🍪 Fechando cookies...")
            cookie_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            self.driver.execute_script("arguments[0].click();", cookie_btn)
            logger.info("✅ Cookies fechados")
            time.sleep(2)
        except Exception as e:
            logger.info("ℹ️ Cookies não encontrados ou já fechados")
        
        # 2. Seletor de Idioma
        try:
            logger.info("🌐 Fechando seletor de idioma...")
            
            # Possíveis seletores de idioma comuns
            language_selectors = [
                "button[aria-label*='language']",
                "button[aria-label*='idioma']",
                "div[class*='language']",
                "div[class*='lang']",
                ".language-selector",
                ".lang-selector",
                "[data-testid*='language']",
                "[data-testid*='lang']",
                "button[title*='language']",
                "button[title*='idioma']"
            ]
            
            for selector in language_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            # Clica fora para fechar ou ESC
                            self.driver.execute_script("arguments[0].style.display = 'none';", elem)
                            logger.info(f"✅ Fechado seletor idioma: {selector}")
                except:
                    continue
            
            # Tenta ESC para fechar qualquer dropdown aberto
            try:
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                logger.info("✅ ESC enviado para fechar dropdowns")
            except:
                pass
                
        except Exception as e:
            logger.info("ℹ️ Seletor de idioma não encontrado")
        
        # 3. Outros overlays genéricos
        try:
            logger.info("🎭 Fechando outros overlays...")
            
            generic_overlays = [
                ".modal-backdrop",
                ".overlay",
                "[style*='z-index: 999']",
                "[style*='z-index: 9999']",
                ".popup",
                ".dropdown-menu.show",
                ".tooltip"
            ]
            
            for selector in generic_overlays:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        self.driver.execute_script("arguments[0].style.display = 'none';", elem)
                        logger.info(f"✅ Overlay removido: {selector}")
                except:
                    continue
                    
        except Exception as e:
            logger.info("ℹ️ Outros overlays não encontrados")
        
        # 4. Aguarda estabilização
        time.sleep(3)  
        logger.info("✅ Todos overlays processados")
    
    def safe_fill_and_submit(self, username, password):
        """Preenchimento e submit seguros"""
        logger.info("📝 Preenchimento seguro...")
        
        try:
            # Procura campos
            logger.info("🔍 Procurando campos...")
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "userId"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            logger.info("✅ Campos encontrados")
            
            # Remove qualquer overlay que possa estar sobre os campos
            self.driver.execute_script("""
                var inputs = document.querySelectorAll('input[name="userId"], input[name="password"]');
                inputs.forEach(function(input) {
                    var rect = input.getBoundingClientRect();
                    var elementsAtPoint = document.elementsFromPoint(rect.left + rect.width/2, rect.top + rect.height/2);
                    elementsAtPoint.forEach(function(el, index) {
                        if (index > 0 && el.tagName !== 'INPUT') {
                            el.style.pointerEvents = 'none';
                        }
                    });
                });
            """)
            
            # Preenche username
            logger.info("👤 Preenchendo username...")
            self.driver.execute_script("arguments[0].focus();", username_field)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].value = arguments[1];", username_field, username)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", username_field)
            logger.info("✅ Username preenchido")
            
            time.sleep(1)
            
            # Preenche password
            logger.info("🔒 Preenchendo password...")
            self.driver.execute_script("arguments[0].focus();", password_field)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].value = arguments[1];", password_field, password)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", password_field)
            logger.info("✅ Password preenchido")
            
            time.sleep(2)
            
            # Submit
            logger.info("🚀 Enviando login...")
            try:
                login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Iniciar')]")
                self.driver.execute_script("arguments[0].click();", login_btn)
                logger.info("✅ Botão clicado")
            except:
                password_field.send_keys(Keys.RETURN)
                logger.info("✅ Enter enviado")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no preenchimento: {e}")
            return False
    
    def monitor_login_result(self):
        """Monitora resultado do login"""
        logger.info("👁️ Monitorando resultado...")
        
        mfa_keywords = ["two", "factor", "authentication", "verify", "code", "sms", "email", "token"]
        
        for i in range(60):  # 60 segundos
            time.sleep(1)
            current_url = self.driver.current_url.lower()
            page_source = self.driver.page_source.lower()
            
            # Log a cada 10s
            if i % 10 == 0:
                logger.info(f"  {i}s - URL: {self.driver.current_url}")
            
            # Sucesso - saiu da página de login
            if "sign-in" not in current_url:
                logger.info(f"🎉 LOGIN REALIZADO após {i}s!")
                return "success"
            
            # MFA detectado
            if any(keyword in page_source for keyword in mfa_keywords):
                logger.info(f"🔑 MFA detectado após {i}s!")
                return "mfa"
            
            # Erro detectado
            if any(error in page_source for error in ["invalid", "incorrect", "failed", "denied", "erro"]):
                logger.warning(f"⚠️ Possível erro após {i}s")
                return "error"
        
        logger.warning("⚠️ Timeout no monitoramento")
        return "timeout"
    
    def handle_mfa_interactive(self):
        """Lida com MFA de forma interativa"""
        logger.info("🔐 MFA DETECTADO!")
        
        print("\n" + "="*60)
        print("🔑 MFA NECESSÁRIO - RESOLVA MANUALMENTE")
        print("="*60)
        print("1. 📱 Verifique seu telefone/email")
        print("2. 🖥️ Complete o MFA no navegador que está aberto")
        print("3. ⌨️ Pressione Enter aqui quando terminar")
        print("="*60)
        
        input("⏳ Pressione Enter após completar o MFA...")
        
        current_url = self.driver.current_url
        logger.info(f"📍 URL após MFA: {current_url}")
        
        if "sign-in" not in current_url.lower():
            logger.info("✅ MFA resolvido!")
            return True
        else:
            logger.warning("⚠️ MFA pode não ter sido resolvido")
            return False
    
    def run_complete_login(self, username, password):
        """Executa login completo"""
        logger.info("🚀 Iniciando login completo...")
        
        try:
            # 1. Acessa página
            logger.info("🌐 Acessando página...")
            self.driver.get("https://trc-techresource.mastercard.com")
            time.sleep(8)  # Aguarda carregamento completo
            
            logger.info(f"📍 URL atual: {self.driver.current_url}")
            
            # 2. Fecha todos os overlays
            self.close_all_overlays()
            
            # 3. Preenche e submete
            if not self.safe_fill_and_submit(username, password):
                return False
            
            # 4. Monitora resultado
            result = self.monitor_login_result()
            
            if result == "success":
                logger.info("🎉 LOGIN COMPLETO COM SUCESSO!")
                return True
                
            elif result == "mfa":
                logger.info("🔐 Necessário completar MFA...")
                return self.handle_mfa_interactive()
                
            elif result == "error":
                logger.error("❌ Erro no login - verifique credenciais")
                return False
                
            else:
                logger.warning("⚠️ Status indefinido")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro geral: {e}")
            return False
    
    def close(self):
        try:
            input("Pressione Enter para fechar o navegador...")
            self.driver.quit()
            logger.info("🔒 Navegador fechado")
        except:
            pass

def main():
    logger.info("🚀 Mastercard Bot - Versão Completa")
    
    username = os.getenv('MASTERCARD_USER')
    password = os.getenv('MASTERCARD_PASS')
    
    if not username or not password:
        logger.error("❌ Configure credenciais no .env")
        return
    
    logger.info(f"🔑 Usuario: {username}")
    
    bot = MastercardCompleteBot()
    
    try:
        success = bot.run_complete_login(username, password)
        
        if success:
            logger.info("🎉 SUCESSO TOTAL! Navegador ficará aberto para exploração")
        else:
            logger.error("❌ Login não realizado")
            
    except KeyboardInterrupt:
        logger.info("⏹️ Interrompido")
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main() 