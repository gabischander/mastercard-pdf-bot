#!/usr/bin/env python3
"""
Mastercard PDF Bot - Versão Simplificada e Robusta
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

# Carrega variáveis do arquivo .env
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class MastercardBot:
    def __init__(self):
        self.download_dir = Path("mastercard_pdfs")
        self.download_dir.mkdir(exist_ok=True)
        
        # Setup Chrome
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("prefs", {
            "download.default_directory": str(self.download_dir.absolute()),
            "download.prompt_for_download": False
        })
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 15)
    
    def take_screenshot(self, name="debug"):
        """Tira screenshot para debug"""
        try:
            screenshot_path = f"{name}_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"📸 Screenshot salvo: {screenshot_path}")
        except Exception as e:
            logger.warning(f"❌ Erro ao salvar screenshot: {e}")
    
    def login(self, username, password):
        """Login no Mastercard"""
        logger.info("🔐 Fazendo login...")
        
        try:
            self.driver.get("https://trc-techresource.mastercard.com/login")
            logger.info(f"📱 Página carregada: {self.driver.title}")
            
            # Screenshot da página inicial
            self.take_screenshot("login_page")
            
            # Aguarda o loading desaparecer
            logger.info("⏳ Aguardando página carregar completamente...")
            for i in range(30):  # Até 30 segundos
                if "Loading application" not in self.driver.page_source:
                    logger.info(f"✅ Loading concluído após {i+1} segundos")
                    break
                time.sleep(1)
            else:
                logger.warning("⚠️ Loading ainda ativo após 30s, continuando...")
            
            # Aguarda mais um pouco após o loading
            time.sleep(3)
            self.take_screenshot("login_page_loaded")
            
            # Fechar modais que podem estar bloqueando
            logger.info("🚪 Fechando modais...")
            
            # 1. Aceitar cookies
            cookie_xpaths = [
                "//button[contains(text(), 'Aceitar Cookies')]",
                "//button[contains(text(), 'Aceitar')]",
                "//button[text()='Aceitar Cookies']",
                "//button[@class and contains(@class, 'accept')]",
                "//button[@id and contains(@id, 'accept')]"
            ]
            
            for xpath in cookie_xpaths:
                try:
                    button = self.driver.find_element(By.XPATH, xpath)
                    logger.info(f"✅ Botão de cookies encontrado: {xpath}")
                    button.click()
                    logger.info("✅ Modal de cookies fechado")
                    time.sleep(2)
                    break
                except Exception as e:
                    logger.debug(f"Xpath não funcionou: {xpath}")
                    continue
            
            # 2. Fechar modal branco (idioma/outro)
            close_selectors = [
                "button[class*='close']",
                ".modal-close",
                "[data-dismiss='modal']",
                "button[aria-label='Close']",
                ".close",
                "[role='button'][aria-label='Close']",
                "button[type='button'][class*='close']"
            ]
            
            close_xpaths = [
                "//button[text()='×']",
                "//button[contains(text(), '×')]",
                "//button[@aria-label='Close']",
                "//button[contains(@class, 'close')]",
                "//*[@role='button' and contains(@aria-label, 'Close')]"
            ]
            
            # Tentar CSS selectors primeiro
            for selector in close_selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"✅ Botão de fechar encontrado: {selector}")
                    button.click()
                    logger.info("✅ Modal fechado")
                    time.sleep(2)
                    break
                except:
                    continue
            
            # Se não funcionou, tentar XPaths
            for xpath in close_xpaths:
                try:
                    button = self.driver.find_element(By.XPATH, xpath)
                    logger.info(f"✅ Botão de fechar encontrado: {xpath}")
                    button.click()
                    logger.info("✅ Modal fechado")
                    time.sleep(2)
                    break
                except:
                    continue
            
            # 3. Tentar clicar no botão "Guardar" do modal de idioma
            guardar_xpaths = [
                "//button[contains(text(), 'Guardar')]",
                "//button[text()='Guardar']",
                "//button[@type='button' and contains(text(), 'Guardar')]"
            ]
            
            for xpath in guardar_xpaths:
                try:
                    button = self.driver.find_element(By.XPATH, xpath)
                    logger.info(f"✅ Botão Guardar encontrado: {xpath}")
                    button.click()
                    logger.info("✅ Modal de idioma fechado via Guardar")
                    time.sleep(2)
                    break
                except:
                    continue
            
            self.take_screenshot("modals_closed")
            
            # Múltiplas tentativas de encontrar os campos de login
            username_selectors = [
                # Específicos do Mastercard Connect em português
                "input[placeholder*='ID do utilizador']",
                "input[placeholder*='Introduza o ID']",
                "input[aria-label*='ID do utilizador']",
                # Seletores gerais
                "input[name='username']",
                "input[id='username']", 
                "input[type='email']",
                "input[placeholder*='email']",
                "input[placeholder*='Email']",
                "input[placeholder*='usuário']",
                "input[placeholder*='user']",
                "input[name='email']",
                "input[name='user']",
                "#email",
                "#username",
                ".email-input",
                ".username-input",
                # Específicos do Mastercard Connect
                "input[data-testid*='email']",
                "input[data-testid*='username']",
                "input[formcontrolname*='email']",
                "input[formcontrolname*='username']",
                "input[aria-label*='email']",
                "input[aria-label*='Email']",
                "input[class*='email']",
                "input[class*='user']"
            ]
            
            password_selectors = [
                # Específicos do Mastercard Connect em português
                "input[placeholder*='senha']",
                "input[placeholder*='Senha']",
                "input[placeholder*='token']",
                "input[placeholder*='Introduza sua senha']",
                "input[aria-label*='senha']",
                "input[aria-label*='Senha']",
                # Seletores gerais
                "input[name='password']",
                "input[id='password']",
                "input[type='password']"
            ]
            
            # Tenta encontrar campo de usuário
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"✅ Campo usuário encontrado: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not username_field:
                logger.error("❌ Campo de usuário não encontrado!")
                self.take_screenshot("login_error")
                return False
            
            # Tenta encontrar campo de senha
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"✅ Campo senha encontrado: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not password_field:
                logger.error("❌ Campo de senha não encontrado!")
                self.take_screenshot("login_error")
                return False
            
            # Preenche credenciais
            logger.info("📝 Preenchendo credenciais...")
            username_field.clear()
            username_field.send_keys(username)
            
            password_field.clear()
            password_field.send_keys(password)
            
            # Procura botão de submit
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                ".login-button",
                "#login-button"
            ]
            
            submit_xpaths = [
                "//button[contains(text(), 'Iniciar sessão')]",
                "//button[text()='Iniciar sessão']",
                "//button[contains(text(), 'Sign In')]",
                "//button[contains(text(), 'Login')]",
                "//input[@type='submit']",
                "//button[@type='submit']"
            ]
            
            submit_button = None
            
            # Tenta CSS selectors primeiro
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"✅ Botão encontrado: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            # Se não encontrou, tenta XPaths
            if not submit_button:
                for xpath in submit_xpaths:
                    try:
                        submit_button = self.driver.find_element(By.XPATH, xpath)
                        logger.info(f"✅ Botão encontrado: {xpath}")
                        break
                    except NoSuchElementException:
                        continue
            
            if submit_button:
                submit_button.click()
                logger.info("🚀 Login enviado!")
            else:
                logger.warning("⚠️ Botão não encontrado, tentando Enter...")
                password_field.send_keys(Keys.RETURN)
            
            time.sleep(5)
            
            # Verifica se login foi bem-sucedido
            current_url = self.driver.current_url
            logger.info(f"📍 URL atual: {current_url}")
            
            if "login" not in current_url.lower():
                logger.info("✅ Login realizado com sucesso!")
                return True
            else:
                logger.warning("⚠️ Ainda na página de login, pode ter erro")
                self.take_screenshot("login_result")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no login: {e}")
            self.take_screenshot("login_exception")
            return False
    
    def collect_pdfs(self, limit=3):
        """Coleta PDFs (versão de teste)"""
        logger.info("📄 Procurando PDFs...")
        
        try:
            # URLs possíveis da seção de documentos
            doc_urls = [
                "https://trc-techresource.mastercard.com/resource-center/documents",
                "https://trc-techresource.mastercard.com/documents",
                "https://trc-techresource.mastercard.com/resources"
            ]
            
            for url in doc_urls:
                try:
                    self.driver.get(url)
                    time.sleep(3)
                    if "404" not in self.driver.page_source:
                        logger.info(f"✅ Página encontrada: {url}")
                        break
                except:
                    continue
            
            self.take_screenshot("documents_page")
            
            # Procura links de PDF
            pdf_links = []
            selectors = [
                "a[href*='.pdf']",
                "a[href*='download']",
                ".document-link",
                ".pdf-link"
            ]
            
            for selector in selectors:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for link in links:
                        href = link.get_attribute("href")
                        if href and (".pdf" in href.lower() or "download" in href.lower()):
                            title = link.text.strip() or link.get_attribute("title") or "Documento PDF"
                            pdf_links.append((title, href, link))
                except:
                    continue
            
            logger.info(f"✅ Encontrados {len(pdf_links)} possíveis PDFs")
            
            if pdf_links:
                # Baixa alguns PDFs (limitado para teste)
                for i, (title, url, element) in enumerate(pdf_links[:limit]):
                    logger.info(f"⬇️ Tentando baixar {i+1}/{limit}: {title[:50]}...")
                    try:
                        element.click()
                        time.sleep(2)
                        logger.info("✅ Download iniciado")
                    except Exception as e:
                        logger.warning(f"❌ Erro ao baixar: {e}")
                
                logger.info("🎉 Processo de download concluído!")
            else:
                logger.warning("⚠️ Nenhum PDF encontrado na página")
                
        except Exception as e:
            logger.error(f"❌ Erro na coleta de PDFs: {e}")
            self.take_screenshot("pdf_collection_error")
    
    def close(self):
        """Fecha navegador"""
        logger.info("🔒 Fechando navegador...")
        self.driver.quit()

def main():
    logger.info("🚀 Iniciando Mastercard PDF Bot...")
    
    # Pega credenciais do .env
    username = os.getenv('MASTERCARD_USER')
    password = os.getenv('MASTERCARD_PASS')
    
    if not username or not password:
        logger.error("❌ Credenciais não encontradas no .env!")
        username = input("Email Mastercard: ")
        password = input("Senha Mastercard: ")
    else:
        logger.info(f"✅ Credenciais carregadas para: {username}")
    
    # Executa bot
    bot = MastercardBot()
    try:
        if bot.login(username, password):
            bot.collect_pdfs(limit=3)  # Teste com 3 PDFs
        else:
            logger.error("❌ Login falhou, abortando...")
    except KeyboardInterrupt:
        logger.info("⏹️ Bot interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()
