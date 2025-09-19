#!/usr/bin/env python3
"""
Mastercard PDF Bot - Híbrido: Login manual + Coleta automática
"""
import os
import time
import logging
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class MastercardHybridBot:
    def __init__(self):
        self.download_dir = Path("mastercard_pdfs")
        self.download_dir.mkdir(exist_ok=True)
        logger.info("✅ Bot Híbrido iniciado")
    
    def open_new_tab_for_login(self):
        """Abre nova aba para login manual"""
        logger.info("🌐 Abrindo nova aba para login...")
        
        try:
            url = "https://trc-techresource.mastercard.com"
            cmd = ["open", "-a", "Google Chrome", url]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Nova aba aberta!")
                return True
            else:
                logger.error(f"❌ Erro: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return False
    
    def wait_for_manual_login(self):
        """Aguarda login manual com 1Password"""
        logger.info("🔑 Aguardando login manual...")
        
        print("\n" + "="*80)
        print("🔑 FAÇA LOGIN COM 1PASSWORD")
        print("="*80)
        print("1. 🖥️ Vá para a nova aba que abriu")
        print("2. 🍪 Feche cookies se aparecer")
        print("3. 🌐 Feche seletor de idioma se aparecer") 
        print("4. 👆 Clique no campo 'ID do utilizador'")
        print("5. 🔑 Use 1Password (Cmd+\\ ou clique no ícone)")
        print("6. 🚀 Complete o login + MFA")
        print("7. ⌨️ Pressione Enter aqui quando estiver LOGADO")
        print("="*80)
        print("💡 Deixe a aba aberta - vou conectar para coletar PDFs!")
        print()
        
        input("⏳ Pressione Enter quando login estiver COMPLETO...")
        
        confirm = input("✅ Confirmação: Login realizado com sucesso? (s/n): ").lower()
        return confirm == 's'
    
    def start_automation_chrome(self):
        """Inicia Chrome para automação"""
        logger.info("🤖 Iniciando Chrome para automação...")
        
        try:
            options = Options()
            options.add_argument("--window-size=1600,1200")
            
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
            
            self.wait = WebDriverWait(self.driver, 30)
            logger.info("✅ Chrome automação iniciado!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return False
    
    def navigate_and_assume_logged_in(self):
        """Navega assumindo que login foi feito"""
        logger.info("🌐 Navegando para coleta...")
        
        try:
            self.driver.get("https://trc-techresource.mastercard.com")
            time.sleep(8)
            
            current_url = self.driver.current_url
            logger.info(f"📍 URL: {current_url}")
            
            # Se ainda na página de login, redireciona
            if "sign-in" in current_url.lower():
                logger.warning("⚠️ Ainda na página de login")
                
                print("\n🔑 Complete o login nesta nova janela também")
                print("(Use 1Password normalmente)")
                input("Pressione Enter quando terminar...")
                
                time.sleep(3)
                current_url = self.driver.current_url
                
                if "sign-in" in current_url.lower():
                    logger.error("❌ Login não detectado")
                    return False
            
            logger.info("✅ Página carregada para coleta!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro navegando: {e}")
            return False
    
    def automatic_pdf_collection(self):
        """Coleta automática de PDFs"""
        logger.info("🤖 Iniciando coleta automática de PDFs...")
        
        try:
            time.sleep(5)  # Aguarda página carregar
            
            # Seletores para encontrar PDFs
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
            
            logger.info("🔍 Procurando PDFs...")
            
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
                            if not any(p['href'] == href for p in found_pdfs if p['href']):
                                found_pdfs.append(pdf_info)
                                logger.info(f"📄 PDF: {pdf_info['text']}")
                except:
                    continue
            
            # Procura também por links de seções
            self.search_document_sections(found_pdfs)
            
            if found_pdfs:
                logger.info(f"✅ {len(found_pdfs)} PDFs encontrados!")
                self.display_and_download_pdfs(found_pdfs)
            else:
                logger.info("⚠️ Nenhum PDF encontrado automaticamente")
                self.try_navigation_exploration()
                
        except Exception as e:
            logger.error(f"❌ Erro na coleta: {e}")
    
    def search_document_sections(self, found_pdfs):
        """Procura seções de documentos"""
        logger.info("📂 Procurando seções de documentos...")
        
        section_keywords = [
            "documentation", "resources", "guides", "downloads", 
            "developer", "technical", "api", "manual"
        ]
        
        for keyword in section_keywords:
            try:
                links = self.driver.find_elements(
                    By.XPATH, 
                    f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]"
                )
                
                for link in links:
                    text = link.text.strip()
                    href = link.get_attribute('href')
                    if text and href:
                        logger.info(f"🔗 Seção: {text} -> {href}")
                        
                        # Pode ter PDFs, adiciona para explorar
                        found_pdfs.append({
                            'element': link,
                            'href': href,
                            'text': f"[SEÇÃO] {text}",
                            'onclick': None
                        })
                        
            except:
                continue
    
    def try_navigation_exploration(self):
        """Tenta explorar navegação automaticamente"""
        logger.info("🧭 Explorando navegação...")
        
        try:
            # Procura por menus principais
            nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "nav, .nav, .menu, .navigation")
            
            for nav in nav_elements:
                try:
                    links = nav.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        text = link.text.strip().lower()
                        if any(keyword in text for keyword in ['doc', 'resource', 'guide', 'download']):
                            href = link.get_attribute('href')
                            logger.info(f"🎯 Link interessante: {link.text.strip()} -> {href}")
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"Erro na exploração: {e}")
        
        # Modo manual como fallback
        self.manual_exploration_mode()
    
    def display_and_download_pdfs(self, pdf_list):
        """Exibe e baixa PDFs"""
        print("\n" + "="*80)
        print("📄 PDFs ENCONTRADOS")
        print("="*80)
        for i, pdf in enumerate(pdf_list, 1):
            print(f"{i:2d}. {pdf['text']}")
            if pdf['href']:
                print(f"     URL: {pdf['href']}")
        print("="*80)
        
        download_all = input("\n💾 Baixar TODOS os PDFs? (s/n): ").lower()
        
        if download_all == 's':
            self.download_pdf_list(pdf_list)
        else:
            print("🔍 Deixando navegador aberto para exploração manual")
            input("Pressione Enter quando terminar...")
    
    def download_pdf_list(self, pdf_list):
        """Baixa lista de PDFs"""
        logger.info(f"💾 Baixando {len(pdf_list)} PDFs...")
        
        success_count = 0
        
        for i, pdf in enumerate(pdf_list, 1):
            try:
                logger.info(f"📥 {i}/{len(pdf_list)}: {pdf['text']}")
                
                if pdf['onclick']:
                    self.driver.execute_script(pdf['onclick'])
                elif pdf['href']:
                    self.driver.execute_script("arguments[0].click();", pdf['element'])
                
                success_count += 1
                time.sleep(3)  # Aguarda download
                
            except Exception as e:
                logger.warning(f"⚠️ Erro: {e}")
        
        logger.info(f"✅ {success_count}/{len(pdf_list)} downloads realizados!")
        logger.info(f"📁 Salvos em: {self.download_dir}")
    
    def manual_exploration_mode(self):
        """Modo exploração manual"""
        print("\n" + "="*80)
        print("🔍 EXPLORAÇÃO MANUAL")
        print("="*80)
        print("O navegador ficará aberto para você explorar:")
        print("• Procure seções 'Documentation', 'Resources'")
        print("• Clique em links que podem ter PDFs")
        print("• Baixe PDFs clicando normalmente")
        print("="*80)
        
        input("⏳ Pressione Enter quando terminar...")
    
    def run_hybrid_session(self):
        """Executa sessão híbrida completa"""
        logger.info("🚀 Iniciando sessão híbrida...")
        
        try:
            # 1. Nova aba para login manual
            if not self.open_new_tab_for_login():
                return False
            
            time.sleep(3)
            
            # 2. Aguarda login manual
            if not self.wait_for_manual_login():
                logger.error("❌ Login não confirmado")
                return False
            
            # 3. Inicia Chrome para automação
            if not self.start_automation_chrome():
                return False
            
            # 4. Navega assumindo login feito
            if not self.navigate_and_assume_logged_in():
                return False
            
            # 5. Coleta automática
            self.automatic_pdf_collection()
            
            logger.info("🎉 Sessão híbrida concluída!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return False
    
    def close(self):
        try:
            if hasattr(self, 'driver'):
                input("\n🔒 Pressione Enter para fechar...")
                self.driver.quit()
                logger.info("✅ Fechado")
        except:
            pass

def main():
    logger.info("🚀 Mastercard Bot - Híbrido")
    
    bot = MastercardHybridBot()
    
    try:
        success = bot.run_hybrid_session()
        
        if success:
            logger.info("🎉 MISSÃO CUMPRIDA!")
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
