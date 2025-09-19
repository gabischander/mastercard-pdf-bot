#!/usr/bin/env python3
"""
Mastercard PDF Bot - Versão Final Corrigida
Corrige URLs e lógica de login
"""
import os
import time
import logging
import requests
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

class MastercardBotFinal:
    def __init__(self, headless=False):
        self.download_dir = Path("mastercard_pdfs")
        self.download_dir.mkdir(exist_ok=True)
        
        # Chrome options
        options = Options()
        if headless:
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Download preferences
        prefs = {
            "download.default_directory": str(self.download_dir.absolute()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True
        }
        options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # Esconde que é um bot
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 15)
        logger.info("✅ Chrome iniciado")
    
    def screenshot(self, name="debug"):
        """Salva screenshot para debug"""
        try:
            path = f"{name}_{int(time.time())}.png"
            self.driver.save_screenshot(path)
            logger.info(f"📸 Screenshot: {path}")
        except Exception as e:
            logger.warning(f"Erro screenshot: {e}")
    
    def wait_and_click(self, selector, timeout=10):
        """Aguarda elemento e clica"""
        try:
            if selector.startswith("//"):
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
            else:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
            element.click()
            return True
        except:
            return False
    
    def login(self, username, password):
        """Login no Mastercard Connect"""
        logger.info("🔐 Iniciando login...")
        
        try:
            # URL correta do Mastercard Connect
            self.driver.get("https://trc-techresource.mastercard.com")
            time.sleep(3)
            self.screenshot("page_loaded")
            
            current_url = self.driver.current_url
            logger.info(f"📍 URL atual: {current_url}")
            
            # Se já está na página de login do MastercardConnect
            if "mastercardconnect.com" in current_url:
                logger.info("✅ Página de login detectada")
                
                # Aguarda página carregar
                time.sleep(3)
                
                # Procura campo de email/username
                username_selectors = [
                    "input[type='email']",
                    "input[name='username']", 
                    "input[name='email']",
                    "input[id*='email']",
                    "input[id*='username']",
                    "input[placeholder*='email']",
                    "input[placeholder*='Email']"
                ]
                
                username_field = None
                for selector in username_selectors:
                    try:
                        field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if field.is_displayed() and field.is_enabled():
                            username_field = field
                            logger.info(f"✅ Campo email encontrado: {selector}")
                            break
                    except:
                        continue
                
                if not username_field:
                    logger.error("❌ Campo de email não encontrado")
                    self.screenshot("no_email_field")
                    return False
                
                # Procura campo de senha
                password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                
                if not password_field:
                    logger.error("❌ Campo de senha não encontrado")
                    self.screenshot("no_password_field")
                    return False
                
                logger.info("✅ Campo de senha encontrado")
                
                # Preenche credenciais
                logger.info("📝 Preenchendo credenciais...")
                username_field.clear()
                username_field.send_keys(username)
                time.sleep(1)
                
                password_field.clear()
                password_field.send_keys(password)
                time.sleep(1)
                
                self.screenshot("credentials_filled")
                
                # Procura botão de login
                login_button = None
                login_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "//button[contains(text(), 'Sign In')]",
                    "//button[contains(text(), 'Sign in')]",
                    "//button[contains(text(), 'Login')]"
                ]
                
                for selector in login_selectors:
                    try:
                        if selector.startswith("//"):
                            button = self.driver.find_element(By.XPATH, selector)
                        else:
                            button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        
                        if button.is_displayed() and button.is_enabled():
                            login_button = button
                            logger.info(f"✅ Botão login encontrado: {selector}")
                            break
                    except:
                        continue
                
                if login_button:
                    login_button.click()
                    logger.info("🚀 Login enviado")
                else:
                    logger.warning("⚠️ Botão não encontrado, usando Enter")
                    password_field.send_keys(Keys.RETURN)
                
                # Aguarda resultado
                time.sleep(5)
                self.screenshot("after_login")
                
                new_url = self.driver.current_url
                logger.info(f"📍 Nova URL: {new_url}")
                
                # Verifica sucesso
                if "sign-in" not in new_url.lower() or "dashboard" in new_url.lower():
                    logger.info("✅ Login realizado com sucesso!")
                    return True
                else:
                    logger.warning("⚠️ Login pode ter falhado")
                    return False
            
            else:
                logger.warning("⚠️ Não redirecionou para página de login")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no login: {e}")
            self.screenshot("login_error")
            return False
    
    def navigate_to_documents(self):
        """Navega para seção de documentos"""
        logger.info("🗂️ Navegando para documentos...")
        
        # Aguarda carregar dashboard
        time.sleep(3)
        
        # Procura por links de documentos/resources
        doc_links = [
            "//a[contains(text(), 'Documents')]",
            "//a[contains(text(), 'Resources')]", 
            "//a[contains(text(), 'Resource Center')]",
            "//a[contains(text(), 'Downloads')]",
            "a[href*='document']",
            "a[href*='resource']"
        ]
        
        for selector in doc_links:
            if self.wait_and_click(selector):
                logger.info(f"✅ Link de documentos clicado: {selector}")
                time.sleep(3)
                self.screenshot("documents_section")
                return True
        
        # Se não encontrou links, tenta URLs diretas
        doc_urls = [
            "https://trc-techresource.mastercard.com/resource-center",
            "https://mastercardconnect.com/documents",
            "https://mastercardconnect.com/resources"
        ]
        
        for url in doc_urls:
            try:
                self.driver.get(url)
                time.sleep(3)
                if "404" not in self.driver.page_source:
                    logger.info(f"✅ Acessou: {url}")
                    self.screenshot("documents_direct")
                    return True
            except:
                continue
        
        logger.warning("⚠️ Seção de documentos não encontrada")
        return False
    
    def find_pdfs(self):
        """Encontra links de PDF na página"""
        logger.info("🔍 Procurando PDFs...")
        
        pdf_elements = []
        
        # Seletores para encontrar PDFs
        selectors = [
            "a[href$='.pdf']",
            "a[href*='.pdf']",
            "a[href*='download']",
            "//a[contains(@href, '.pdf')]",
            "//a[contains(text(), 'PDF')]",
            "//a[contains(text(), 'Download')]"
        ]
        
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    elements = self.driver.find_elements(By.XPATH, selector)
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for elem in elements:
                    if elem.is_displayed():
                        href = elem.get_attribute("href")
                        text = elem.text.strip()
                        
                        if href and (".pdf" in href.lower() or "download" in href.lower()):
                            pdf_elements.append({
                                'element': elem,
                                'url': href,
                                'title': text or "PDF Document"
                            })
            except:
                continue
        
        # Remove duplicatas por URL
        unique_pdfs = []
        seen_urls = set()
        for pdf in pdf_elements:
            if pdf['url'] not in seen_urls:
                unique_pdfs.append(pdf)
                seen_urls.add(pdf['url'])
        
        logger.info(f"✅ Encontrados {len(unique_pdfs)} PDFs")
        return unique_pdfs
    
    def download_pdfs(self, pdf_list, limit=5):
        """Baixa os PDFs encontrados"""
        logger.info(f"⬇️ Iniciando downloads (máximo {limit})...")
        
        downloaded = 0
        
        for i, pdf in enumerate(pdf_list[:limit]):
            logger.info(f"📄 Download {i+1}/{min(len(pdf_list), limit)}: {pdf['title'][:50]}...")
            
            try:
                # Método 1: Clique no elemento
                self.driver.execute_script("arguments[0].click();", pdf['element'])
                time.sleep(2)
                downloaded += 1
                logger.info("✅ Download iniciado")
                
            except Exception as e:
                logger.warning(f"❌ Erro no download: {e}")
                
                # Método 2: Download direto se possível
                try:
                    response = requests.get(pdf['url'], timeout=10)
                    if response.status_code == 200:
                        filename = f"document_{i+1}.pdf"
                        filepath = self.download_dir / filename
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        logger.info(f"✅ Download direto: {filename}")
                        downloaded += 1
                except:
                    logger.warning("❌ Download direto também falhou")
        
        return downloaded
    
    def run(self, username, password, pdf_limit=5):
        """Executa o processo completo"""
        logger.info("🚀 Iniciando processo completo...")
        
        try:
            # 1. Login
            if not self.login(username, password):
                logger.error("❌ Falha no login")
                return False
            
            # 2. Navegar para documentos
            if not self.navigate_to_documents():
                logger.error("❌ Falha ao acessar documentos")
                return False
            
            # 3. Encontrar PDFs
            pdfs = self.find_pdfs()
            if not pdfs:
                logger.warning("⚠️ Nenhum PDF encontrado")
                return False
            
            # 4. Baixar PDFs
            downloaded = self.download_pdfs(pdfs, pdf_limit)
            
            logger.info(f"🎉 Processo concluído! {downloaded} PDFs baixados")
            return downloaded > 0
            
        except Exception as e:
            logger.error(f"❌ Erro no processo: {e}")
            return False
    
    def close(self):
        """Fecha o navegador"""
        try:
            self.driver.quit()
            logger.info("🔒 Navegador fechado")
        except:
            pass

def main():
    logger.info("🚀 Mastercard PDF Bot - Versão Final")
    
    # Credenciais
    username = os.getenv('MASTERCARD_USER')
    password = os.getenv('MASTERCARD_PASS')
    
    if not username or not password:
        logger.error("❌ Configure MASTERCARD_USER e MASTERCARD_PASS no .env")
        username = input("Email: ")
        password = input("Senha: ")
    
    # Executar bot
    bot = MastercardBotFinal(headless=False)
    
    try:
        success = bot.run(username, password, pdf_limit=5)
        if success:
            logger.info("🎉 Sucesso! Verifique a pasta mastercard_pdfs/")
        else:
            logger.error("❌ Processo falhou")
    
    except KeyboardInterrupt:
        logger.info("⏹️ Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()
