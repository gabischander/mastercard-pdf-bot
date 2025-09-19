#!/usr/bin/env python3
"""
Mastercard PDF Bot - Usando SEU Chrome com 1Password
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

class MastercardUserChromeBot:
    def __init__(self):
        self.download_dir = Path("mastercard_pdfs")
        self.download_dir.mkdir(exist_ok=True)
        
        options = Options()
        
        # USA SEU PERFIL DO CHROME (com 1Password instalado!)
        user_data_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome")
        options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # Usa um perfil específico (ou Default)
        options.add_argument("--profile-directory=Default")
        
        # Configurações mais naturais
        options.add_argument("--window-size=1600,1200")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        
        # Não desabilita extensões (mantém 1Password)
        # options.add_argument("--disable-extensions")  # REMOVIDO!
        
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
        
        self.wait = WebDriverWait(self.driver, 60)
        logger.info("✅ Chrome com SEU perfil iniciado (1Password disponível)")
    
    def navigate_and_clean(self):
        """Navega e limpa página"""
        logger.info("🌐 Navegando para Mastercard...")
        
        try:
            # Vai direto para login
            self.driver.get("https://trc-techresource.mastercard.com")
            time.sleep(10)  # Aguarda carregar completamente
            
            logger.info(f"📍 URL: {self.driver.current_url}")
            
            # Fecha cookies
            try:
                logger.info("🍪 Fechando cookies...")
                cookie_btn = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                )
                cookie_btn.click()
                logger.info("✅ Cookies fechados")
                time.sleep(3)
            except:
                logger.info("ℹ️ Cookies não encontrados")
            
            # Fecha seletor de idioma
            try:
                logger.info("🌐 Fechando seletor de idioma...")
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ESCAPE)
                body.click()  # Clica fora
                time.sleep(3)
                logger.info("✅ Seletor fechado")
            except:
                logger.info("ℹ️ Seletor já fechado")
            
            # Aguarda campos aparecerem
            logger.info("⏳ Aguardando campos de login...")
            
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "userId"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            logger.info("✅ Campos encontrados")
            
            # Clica no username para 1Password detectar
            logger.info("🔑 Ativando detecção do 1Password...")
            username_field.click()
            time.sleep(2)
            
            logger.info("✅ Página pronta para 1Password!")
            
        except Exception as e:
            logger.error(f"❌ Erro na navegação: {e}")
    
    def wait_for_1password_login(self):
        """Aguarda login com 1Password"""
        logger.info("🔐 Aguardando login com 1Password...")
        
        print("\n" + "="*80)
        print("🔑 1PASSWORD DEVE ESTAR DISPONÍVEL AGORA!")
        print("="*80)
        print("1. 🖥️ Vá para o navegador")
        print("2. 👆 Clique no campo de username")
        print("3. 🔑 Você DEVE ver o ícone do 1Password no campo!")
        print("4. 🖱️ Clique no ícone ou use Cmd+\\ para 1Password")
        print("5. 🔐 Selecione suas credenciais Mastercard")
        print("6. 🚀 Faça login normalmente")
        print("7. 📱 Complete MFA se necessário")
        print("8. ⌨️ Pressione Enter aqui quando logado")
        print("="*80)
        print("💡 Se não ver o ícone, pode ser que o perfil não esteja correto")
        print()
        
        start_url = self.driver.current_url
        
        # Aguarda confirmação do usuário
        input("⏳ Pressione Enter após fazer login com 1Password...")
        
        # Verifica se login foi realizado
        current_url = self.driver.current_url
        
        if current_url != start_url and "sign-in" not in current_url.lower():
            logger.info(f"🎉 LOGIN DETECTADO!")
            logger.info(f"📍 URL: {current_url}")
            return True
        else:
            # Dá segunda chance
            confirm = input("❓ Login foi realizado? (s/n): ").lower()
            return confirm == 's'
    
    def collect_pdfs(self):
        """Coleta PDFs após login"""
        logger.info("�� Coletando PDFs...")
        
        try:
            time.sleep(5)  # Aguarda página carregar
            
            # Procura PDFs
            pdf_links = []
            selectors = [
                "a[href$='.pdf']",
                "a[href*='pdf']",
                "a[title*='PDF']",
                "*[onclick*='pdf']"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        href = elem.get_attribute('href')
                        text = elem.text.strip()
                        if href and text:
                            pdf_links.append({'href': href, 'text': text, 'element': elem})
                            logger.info(f"📄 PDF: {text}")
                except:
                    continue
            
            if pdf_links:
                logger.info(f"✅ {len(pdf_links)} PDFs encontrados!")
                
                download = input(f"\n💾 Baixar {len(pdf_links)} PDFs? (s/n): ").lower()
                
                if download == 's':
                    for i, pdf in enumerate(pdf_links, 1):
                        try:
                            logger.info(f"📥 {i}/{len(pdf_links)}: {pdf['text']}")
                            pdf['element'].click()
                            time.sleep(3)
                        except Exception as e:
                            logger.warning(f"⚠️ Erro: {e}")
                    
                    logger.info("✅ Downloads concluídos!")
            else:
                logger.info("⚠️ Nenhum PDF encontrado automaticamente")
                print("\n🔍 Explore manualmente no navegador")
                
        except Exception as e:
            logger.error(f"❌ Erro coletando PDFs: {e}")
    
    def run_session(self):
        """Executa sessão completa"""
        logger.info("🚀 Iniciando sessão com SEU Chrome...")
        
        try:
            # 1. Navega e limpa
            self.navigate_and_clean()
            
            # 2. Aguarda login com 1Password
            login_success = self.wait_for_1password_login()
            
            if login_success:
                logger.info("🎉 LOGIN REALIZADO!")
                
                # 3. Coleta PDFs
                self.collect_pdfs()
                
                return True
            else:
                logger.error("❌ Login não realizado")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro na sessão: {e}")
            return False
    
    def close(self):
        try:
            input("\n🔒 Pressione Enter para fechar...")
            self.driver.quit()
            logger.info("✅ Fechado")
        except:
            pass

def main():
    logger.info("🚀 Mastercard Bot - SEU Chrome + 1Password")
    
    bot = MastercardUserChromeBot()
    
    try:
        success = bot.run_session()
        
        if success:
            logger.info("🎉 SUCESSO!")
        else:
            logger.error("❌ Falha na sessão")
            
    except KeyboardInterrupt:
        logger.info("⏹️ Interrompido")
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()
