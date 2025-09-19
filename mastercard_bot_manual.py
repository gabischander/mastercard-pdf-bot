#!/usr/bin/env python3
"""
Mastercard PDF Bot - Semi-Automático (Limpa overlays + Login manual)
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

class MastercardManualBot:
    def __init__(self):
        self.download_dir = Path("mastercard_pdfs")
        self.download_dir.mkdir(exist_ok=True)
        
        options = Options()
        # NAVEGADOR VISÍVEL E GRANDE
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15")
        options.add_argument("--window-size=1600,1200")
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
        
        self.wait = WebDriverWait(self.driver, 45)
        logger.info("✅ Chrome VISÍVEL iniciado - Modo Manual")
    
    def clean_page_for_manual_login(self):
        """Limpa página mas deixa pronta para login manual"""
        logger.info("🧹 Limpando página para login manual...")
        
        # 1. Fecha cookies
        try:
            logger.info("🍪 Fechando cookies...")
            cookie_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            self.driver.execute_script("arguments[0].click();", cookie_btn)
            logger.info("✅ Cookies fechados")
            time.sleep(2)
        except:
            logger.info("ℹ️ Cookies não encontrados")
        
        # 2. Fecha seletor de idioma
        try:
            logger.info("🌐 Fechando seletor de idioma...")
            
            # Tenta ESC para fechar dropdowns
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(1)
            
            # Remove overlays de idioma específicos
            language_overlays = [
                "div[class*='language']",
                "div[class*='lang']", 
                ".dropdown-menu.show",
                "[aria-expanded='true']"
            ]
            
            for selector in language_overlays:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            self.driver.execute_script("arguments[0].style.display = 'none';", elem)
                            logger.info(f"✅ Overlay idioma removido: {selector}")
                except:
                    continue
                    
            logger.info("✅ Seletor de idioma processado")
        except:
            logger.info("ℹ️ Seletor de idioma não encontrado")
        
        # 3. Remove overlays genéricos que podem atrapalhar
        try:
            logger.info("🎭 Removendo overlays genéricos...")
            
            generic_overlays = [
                ".modal-backdrop",
                ".loading-overlay",
                ".spinner",
                ".tooltip"
            ]
            
            for selector in generic_overlays:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        self.driver.execute_script("arguments[0].style.display = 'none';", elem)
                except:
                    continue
                    
        except:
            pass
        
        # 4. Aguarda estabilização
        time.sleep(3)
        logger.info("✅ Página limpa para login manual!")
    
    def wait_for_manual_login(self):
        """Aguarda usuário fazer login manualmente"""
        logger.info("⏳ Aguardando login manual...")
        
        print("\n" + "="*70)
        print("🔑 PÁGINA LIMPA - FAÇA LOGIN MANUALMENTE")
        print("="*70)
        print("1. 🖥️ Use o navegador que abriu")
        print("2. 🔐 Use seu 1Password normalmente") 
        print("3. 📱 Complete qualquer MFA necessário")
        print("4. ⌨️ Pressione Enter aqui quando estiver logado")
        print("="*70)
        print("💡 Dica: Os overlays foram removidos, campos devem estar clicáveis!")
        print()
        
        # Monitora automaticamente enquanto aguarda
        start_url = self.driver.current_url
        
        input("⏳ Pressione Enter após fazer login...")
        
        current_url = self.driver.current_url
        if current_url != start_url and "sign-in" not in current_url.lower():
            logger.info(f"🎉 LOGIN DETECTADO!")
            logger.info(f"📍 Nova URL: {current_url}")
            return True
        else:
            logger.warning("⚠️ URL não mudou, verificando...")
            return False
    
    def confirm_login_success(self):
        """Confirma se login foi bem-sucedido"""
        current_url = self.driver.current_url
        logger.info(f"📍 URL atual: {current_url}")
        
        # Verifica se saiu da página de login
        if "sign-in" not in current_url.lower():
            logger.info("✅ Login confirmado com sucesso!")
            return True
        else:
            logger.warning("⚠️ Ainda na página de login")
            return False
    
    def explore_site_for_pdfs(self):
        """Explora site procurando PDFs"""
        logger.info("🔍 Explorando site para encontrar PDFs...")
        
        try:
            # Aguarda página carregar
            time.sleep(5)
            
            # Procura por links de documentos/PDFs
            logger.info("📄 Procurando links de PDF...")
            
            # Possíveis seletores para PDFs
            pdf_selectors = [
                "a[href$='.pdf']",
                "a[href*='pdf']",
                "a[title*='PDF']",
                "a[title*='document']",
                "[download*='.pdf']"
            ]
            
            all_pdf_links = []
            
            for selector in pdf_selectors:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for link in links:
                        href = link.get_attribute('href')
                        text = link.text.strip()
                        if href and href not in [l['href'] for l in all_pdf_links]:
                            all_pdf_links.append({
                                'href': href,
                                'text': text,
                                'element': link
                            })
                            logger.info(f"📄 PDF encontrado: {text} -> {href}")
                except:
                    continue
            
            if all_pdf_links:
                logger.info(f"✅ Total de {len(all_pdf_links)} PDFs encontrados!")
                
                print("\n" + "="*70)
                print("📄 PDFs ENCONTRADOS")
                print("="*70)
                for i, pdf in enumerate(all_pdf_links, 1):
                    print(f"{i}. {pdf['text']} -> {pdf['href']}")
                print("="*70)
                
                # Pergunta se quer baixar
                download = input("\n💾 Baixar todos os PDFs? (s/n): ").lower().strip()
                
                if download == 's':
                    self.download_pdfs(all_pdf_links)
                else:
                    logger.info("📋 Lista de PDFs salva, download cancelado")
            else:
                logger.info("⚠️ Nenhum PDF encontrado automaticamente")
                logger.info("🔍 Explore manualmente no navegador")
            
        except Exception as e:
            logger.error(f"❌ Erro na exploração: {e}")
    
    def download_pdfs(self, pdf_links):
        """Baixa lista de PDFs"""
        logger.info(f"💾 Iniciando download de {len(pdf_links)} PDFs...")
        
        for i, pdf in enumerate(pdf_links, 1):
            try:
                logger.info(f"📥 Baixando {i}/{len(pdf_links)}: {pdf['text']}")
                
                # Clica no link para baixar
                self.driver.execute_script("arguments[0].click();", pdf['element'])
                
                # Aguarda download
                time.sleep(3)
                
            except Exception as e:
                logger.warning(f"⚠️ Erro baixando {pdf['text']}: {e}")
        
        logger.info("✅ Downloads concluídos!")
    
    def run_manual_session(self):
        """Executa sessão manual completa"""
        logger.info("🚀 Iniciando sessão manual...")
        
        try:
            # 1. Abre página
            logger.info("🌐 Abrindo Mastercard...")
            self.driver.get("https://trc-techresource.mastercard.com")
            time.sleep(5)
            
            # 2. Limpa overlays
            self.clean_page_for_manual_login()
            
            # 3. Aguarda login manual
            login_success = self.wait_for_manual_login()
            
            if not login_success:
                # Dá uma segunda chance
                manual_confirm = input("❓ Você conseguiu fazer login? (s/n): ").lower().strip()
                login_success = (manual_confirm == 's')
            
            if login_success:
                # 4. Confirma login
                if self.confirm_login_success():
                    logger.info("🎉 LOGIN MANUAL BEM-SUCEDIDO!")
                    
                    # 5. Explora PDFs
                    self.explore_site_for_pdfs()
                    
                else:
                    logger.warning("⚠️ Login pode não ter sido concluído")
            else:
                logger.error("❌ Login manual não foi realizado")
            
            return login_success
            
        except Exception as e:
            logger.error(f"❌ Erro na sessão: {e}")
            return False
    
    def close(self):
        try:
            input("\n🔒 Pressione Enter para fechar o navegador...")
            self.driver.quit()
            logger.info("✅ Navegador fechado")
        except:
            pass

def main():
    logger.info("🚀 Mastercard Bot - Modo Manual")
    
    bot = MastercardManualBot()
    
    try:
        success = bot.run_manual_session()
        
        if success:
            logger.info("🎉 SESSÃO CONCLUÍDA COM SUCESSO!")
        else:
            logger.error("❌ Sessão não foi concluída")
            
    except KeyboardInterrupt:
        logger.info("⏹️ Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()
