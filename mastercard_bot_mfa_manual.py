#!/usr/bin/env python3
"""
Mastercard PDF Bot - MFA Manual
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

class MastercardMFABot:
    def __init__(self):
        self.download_dir = Path("mastercard_pdfs")
        self.download_dir.mkdir(exist_ok=True)
        
        options = Options()
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15")
        
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
        logger.info("✅ Chrome iniciado (modo MFA manual)")
    
    def handle_mfa_manually(self):
        """Pausa para MFA manual"""
        logger.info("🔐 MFA DETECTADO!")
        logger.info("📱 Verifique seu telefone/email para código MFA")
        logger.info("🖥️ Complete o MFA manualmente no navegador")
        
        print("\n" + "="*50)
        print("🔑 MFA DETECTADO - INTERVENÇÃO NECESSÁRIA")
        print("="*50)
        print("1. Verifique seu telefone/email")
        print("2. Digite o código MFA no navegador")
        print("3. Complete o processo de autenticação")
        print("4. Pressione Enter aqui quando terminar")
        print("="*50)
        
        input("⏳ Pressione Enter após completar o MFA...")
        
        # Verifica se login foi bem-sucedido
        current_url = self.driver.current_url
        logger.info(f"📍 URL após MFA: {current_url}")
        
        if "sign-in" not in current_url.lower():
            logger.info("✅ MFA resolvido com sucesso!")
            return True
        else:
            logger.warning("⚠️ Parece que MFA não foi resolvido")
            return False
    
    def wait_for_mfa_or_success(self, timeout=120):
        """Aguarda MFA ou sucesso no login"""
        logger.info("⏳ Aguardando MFA ou sucesso no login...")
        
        mfa_keywords = ["two", "factor", "authentication", "verify", "code", "sms", "email", "token"]
        
        for i in range(timeout):
            time.sleep(1)
            current_url = self.driver.current_url.lower()
            page_source = self.driver.page_source.lower()
            
            # Log periódico
            if i % 10 == 0:
                logger.info(f"  {i}s - Monitorando: {self.driver.current_url}")
            
            # Sucesso - saiu da página de login
            if "sign-in" not in current_url:
                logger.info(f"✅ Login realizado com sucesso após {i}s!")
                return "success"
            
            # MFA detectado
            if any(keyword in page_source for keyword in mfa_keywords):
                logger.info(f"🔑 MFA detectado após {i}s!")
                return "mfa"
            
            # Verifica erros de login
            if any(error in page_source for error in ["invalid", "incorrect", "failed", "denied"]):
                logger.warning(f"⚠️ Possível erro de login após {i}s")
                return "error"
        
        logger.warning("⚠️ Timeout - não foi possível determinar status")
        return "timeout"
    
    def login_with_mfa_support(self, username, password):
        """Login com suporte a MFA"""
        logger.info("🔐 Login com suporte MFA...")
        
        try:
            # Acessa página
            logger.info("🌐 Acessando página...")
            self.driver.get("https://trc-techresource.mastercard.com")
            time.sleep(5)
            
            # Fecha cookies
            try:
                cookie_btn = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                )
                self.driver.execute_script("arguments[0].click();", cookie_btn)
                logger.info("✅ Cookies fechados")
                time.sleep(2)
            except:
                logger.info("ℹ️ Cookies não encontrados")
            
            # Procura campos
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "userId"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            # Preenche credenciais
            logger.info("📝 Preenchendo credenciais...")
            
            self.driver.execute_script("arguments[0].value = arguments[1];", username_field, username)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", username_field)
            
            self.driver.execute_script("arguments[0].value = arguments[1];", password_field, password)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", password_field)
            
            logger.info("✅ Credenciais preenchidas")
            time.sleep(2)
            
            # Submete login
            try:
                login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Iniciar')]")
                self.driver.execute_script("arguments[0].click();", login_btn)
                logger.info("✅ Botão de login clicado")
            except:
                password_field.send_keys(Keys.RETURN)
                logger.info("✅ Enter enviado")
            
            # Aguarda resposta
            status = self.wait_for_mfa_or_success()
            
            if status == "success":
                logger.info("🎉 Login realizado sem MFA!")
                return True
                
            elif status == "mfa":
                logger.info("🔐 MFA necessário - iniciando processo manual")
                return self.handle_mfa_manually()
                
            elif status == "error":
                logger.error("❌ Erro no login - verifique credenciais")
                return False
                
            else:
                logger.warning("⚠️ Status indefinido")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no login: {e}")
            return False
    
    def collect_pdfs(self):
        """Coleta PDFs após login bem-sucedido"""
        logger.info("📄 Iniciando coleta de PDFs...")
        
        try:
            # Aqui você implementaria a navegação para coletar PDFs
            # Por exemplo:
            # 1. Navegar para seção de documentos
            # 2. Encontrar PDFs
            # 3. Fazer download
            
            logger.info("🔍 Procurando PDFs...")
            # Implementar lógica de coleta aqui
            
            logger.info("✅ Coleta de PDFs concluída!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na coleta: {e}")
            return False
    
    def close(self):
        try:
            self.driver.quit()
            logger.info("🔒 Navegador fechado")
        except:
            pass

def main():
    logger.info("🚀 Mastercard Bot - MFA Manual")
    
    username = os.getenv('MASTERCARD_USER')
    password = os.getenv('MASTERCARD_PASS')
    
    if not username or not password:
        logger.error("❌ Configure credenciais no .env")
        return
    
    logger.info(f"🔑 Usando: {username}")
    
    bot = MastercardMFABot()
    
    try:
        # Realiza login
        login_success = bot.login_with_mfa_support(username, password)
        
        if login_success:
            logger.info("🎉 LOGIN REALIZADO COM SUCESSO!")
            
            # Coleta PDFs
            bot.collect_pdfs()
            
            input("Pressione Enter para fechar...")
        else:
            logger.error("❌ Login falhou")
    
    except KeyboardInterrupt:
        logger.info("⏹️ Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main() 