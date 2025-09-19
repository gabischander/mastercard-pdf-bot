#!/usr/bin/env python3
"""
Mastercard PDF Bot - Otimizado para 1Password
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

class Mastercard1PasswordBot:
    def __init__(self):
        self.download_dir = Path("mastercard_pdfs")
        self.download_dir.mkdir(exist_ok=True)
        
        options = Options()
        # NAVEGADOR MAIS "HUMANO" para 1Password
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_argument("--window-size=1600,1200")
        
        # Menos flags "bot-like" para não interferir com 1Password
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Permitir extensões (1Password)
        options.add_argument("--disable-extensions-except")
        options.add_argument("--load-extension")
        
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
        
        # Remove automation detection
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 60)
        logger.info("✅ Chrome iniciado - Modo 1Password")
    
    def navigate_naturally_to_login(self):
        """Navega naturalmente até página de login"""
        logger.info("🧭 Navegação natural para login...")
        
        try:
            # 1. Vai para página principal primeiro (como humano faria)
            logger.info("🏠 Acessando página principal...")
            self.driver.get("https://www.mastercard.com")
            time.sleep(5)
            
            # 2. Vai para trc-techresource (como se fosse redirect)
            logger.info("🔗 Redirecionando para TRC...")
            self.driver.get("https://trc-techresource.mastercard.com")
            time.sleep(8)  # Aguarda carregamento completo
            
            logger.info(f"📍 URL final: {self.driver.current_url}")
            
        except Exception as e:
            logger.error(f"❌ Erro na navegação: {e}")
    
    def prepare_page_for_1password(self):
        """Prepara página para 1Password detectar"""
        logger.info("🔑 Preparando página para 1Password...")
        
        # 1. Fecha cookies sem pressa
        try:
            logger.info("🍪 Fechando cookies...")
            cookie_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            
            # Simula hover antes de clicar (mais humano)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", cookie_btn)
            time.sleep(2)
            self.driver.execute_script("arguments[0].click();", cookie_btn)
            logger.info("✅ Cookies fechados")
            time.sleep(3)
            
        except:
            logger.info("ℹ️ Cookies não encontrados")
        
        # 2. Fecha seletor de idioma gentilmente
        try:
            logger.info("�� Fechando seletor de idioma...")
            
            # ESC para fechar qualquer dropdown
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ESCAPE)
            time.sleep(2)
            
            # Clica fora para garantir que fechou
            body.click()
            time.sleep(2)
            
            logger.info("✅ Seletor de idioma fechado")
            
        except:
            logger.info("ℹ️ Seletor já fechado")
        
        # 3. Aguarda campos estabilizarem para 1Password detectar
        logger.info("⏳ Aguardando campos estabilizarem para 1Password...")
        
        try:
            # Aguarda campos aparecerem
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "userId"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            logger.info("✅ Campos de login detectados")
            
            # Simula "olhar" nos campos (foco + unfocus)
            # Isso ajuda 1Password a detectar
            self.driver.execute_script("arguments[0].focus();", username_field)
            time.sleep(1)
            self.driver.execute_script("arguments[0].blur();", username_field)
            
            self.driver.execute_script("arguments[0].focus();", password_field)
            time.sleep(1)
            self.driver.execute_script("arguments[0].blur();", password_field)
            
            # Clica no username para 1Password detectar
            username_field.click()
            time.sleep(2)
            
            logger.info("✅ Campos preparados para 1Password")
            
        except Exception as e:
            logger.warning(f"⚠️ Erro preparando campos: {e}")
    
    def wait_for_1password_login(self):
        """Aguarda usuário usar 1Password"""
        logger.info("⏳ Aguardando login via 1Password...")
        
        print("\n" + "="*80)
        print("🔑 PÁGINA PRONTA PARA 1PASSWORD")
        print("="*80)
        print("1. 🖥️ Vá para o navegador que abriu")
        print("2. 🔐 Clique no campo de username")
        print("3. 📱 Use 1Password para preencher (Cmd+\\)")
        print("4. 🚀 Faça login normalmente")
        print("5. 📱 Complete MFA se necessário")
        print("6. ⌨️ Pressione Enter aqui quando estiver logado")
        print("="*80)
        print("💡 Dica: Se 1Password não aparecer, tente clicar nos campos")
        print()
        
        # Monitora mudanças na URL
        start_url = self.driver.current_url
        
        # Aguarda input do usuário
        input("⏳ Pressione Enter quando login estiver completo...")
        
        # Verifica se login foi realizado
        current_url = self.driver.current_url
        
        if current_url != start_url and "sign-in" not in current_url.lower():
            logger.info(f"🎉 LOGIN DETECTADO!")
            logger.info(f"📍 Nova URL: {current_url}")
            return True
        else:
            logger.warning("⚠️ URL não mudou")
            
            # Dá segunda chance
            confirm = input("❓ Login foi realizado com sucesso? (s/n): ").lower()
            return confirm == 's'
    
    def find_and_download_pdfs(self):
        """Encontra e baixa PDFs"""
        logger.info("📄 Procurando PDFs no site...")
        
        try:
            # Aguarda página pós-login carregar
            time.sleep(5)
            
            # Procura links de PDF
            pdf_selectors = [
                "a[href$='.pdf']",
                "a[href*='pdf']", 
                "a[href*='PDF']",
                "a[title*='PDF']",
                "a[title*='pdf']",
                "a[download*='.pdf']",
                "*[onclick*='pdf']",
                "*[onclick*='PDF']"
            ]
            
            found_pdfs = []
            
            for selector in pdf_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        href = elem.get_attribute('href')
                        text = elem.text.strip()
                        onclick = elem.get_attribute('onclick')
                        
                        if href or onclick:
                            pdf_info = {
                                'element': elem,
                                'href': href,
                                'text': text or 'PDF sem título',
                                'onclick': onclick
                            }
                            
                            # Evita duplicatas
                            if not any(p['href'] == href for p in found_pdfs):
                                found_pdfs.append(pdf_info)
                                logger.info(f"📄 PDF: {pdf_info['text']} -> {href}")
                except:
                    continue
            
            # Também procura por seções/menus que podem conter PDFs
            logger.info("🔍 Procurando seções de documentos...")
            
            doc_keywords = ["document", "resource", "guide", "manual", "spec", "technical"]
            
            for keyword in doc_keywords:
                try:
                    links = self.driver.find_elements(By.XPATH, f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]")
                    for link in links:
                        text = link.text.strip()
                        href = link.get_attribute('href')
                        if text and href:
                            logger.info(f"🔗 Seção encontrada: {text} -> {href}")
                except:
                    continue
            
            if found_pdfs:
                logger.info(f"✅ {len(found_pdfs)} PDFs encontrados!")
                
                print("\n" + "="*70)
                print("📄 PDFs ENCONTRADOS")
                print("="*70)
                for i, pdf in enumerate(found_pdfs, 1):
                    print(f"{i}. {pdf['text']}")
                    print(f"   URL: {pdf['href']}")
                print("="*70)
                
                # Pergunta sobre download
                download = input("\n💾 Baixar todos os PDFs? (s/n): ").lower()
                
                if download == 's':
                    self.download_all_pdfs(found_pdfs)
                else:
                    logger.info("📋 Lista salva, downloads cancelados")
            else:
                logger.info("⚠️ Nenhum PDF encontrado automaticamente")
                
                print("\n" + "="*70)
                print("🔍 EXPLORE MANUALMENTE")
                print("="*70)
                print("Navegue pelo site no navegador para encontrar PDFs")
                print("O navegador ficará aberto para exploração manual")
                print("="*70)
                
        except Exception as e:
            logger.error(f"❌ Erro na busca por PDFs: {e}")
    
    def download_all_pdfs(self, pdf_list):
        """Baixa todos os PDFs da lista"""
        logger.info(f"💾 Baixando {len(pdf_list)} PDFs...")
        
        for i, pdf in enumerate(pdf_list, 1):
            try:
                logger.info(f"📥 {i}/{len(pdf_list)}: {pdf['text']}")
                
                if pdf['onclick']:
                    # Se tem onclick, executa JavaScript
                    self.driver.execute_script(pdf['onclick'])
                else:
                    # Se tem href, clica no link
                    self.driver.execute_script("arguments[0].click();", pdf['element'])
                
                # Aguarda download
                time.sleep(4)
                
            except Exception as e:
                logger.warning(f"⚠️ Erro baixando {pdf['text']}: {e}")
        
        logger.info("✅ Downloads concluídos!")
    
    def run_1password_session(self):
        """Executa sessão otimizada para 1Password"""
        logger.info("🚀 Sessão 1Password iniciada...")
        
        try:
            # 1. Navega naturalmente
            self.navigate_naturally_to_login()
            
            # 2. Prepara página para 1Password
            self.prepare_page_for_1password()
            
            # 3. Aguarda login via 1Password
            login_success = self.wait_for_1password_login()
            
            if login_success:
                logger.info("🎉 LOGIN VIA 1PASSWORD REALIZADO!")
                
                # 4. Procura e baixa PDFs
                self.find_and_download_pdfs()
                
                return True
            else:
                logger.error("❌ Login via 1Password não realizado")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro na sessão: {e}")
            return False
    
    def close(self):
        try:
            input("\n🔒 Pressione Enter para fechar navegador...")
            self.driver.quit()
            logger.info("✅ Navegador fechado")
        except:
            pass

def main():
    logger.info("🚀 Mastercard Bot - 1Password Edition")
    
    bot = Mastercard1PasswordBot()
    
    try:
        success = bot.run_1password_session()
        
        if success:
            logger.info("🎉 SESSÃO 1PASSWORD CONCLUÍDA!")
        else:
            logger.error("❌ Sessão não concluída")
            
    except KeyboardInterrupt:
        logger.info("⏹️ Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()
