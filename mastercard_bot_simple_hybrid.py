#!/usr/bin/env python3
"""
Mastercard PDF Bot - Híbrido Simples (Instrução manual + Auto coleta)
"""
import os
import time
import logging
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

class MastercardSimpleHybridBot:
    def __init__(self):
        self.download_dir = Path("mastercard_pdfs") 
        self.download_dir.mkdir(exist_ok=True)
        logger.info("✅ Bot Híbrido Simples iniciado")
    
    def instruct_manual_login(self):
        """Instrui login manual no Chrome do usuário"""
        logger.info("📋 Instruindo login manual...")
        
        print("\n" + "="*80)
        print("🔑 FAÇA LOGIN MANUALMENTE NO SEU CHROME")
        print("="*80)
        print("1. 🖥️ Abra seu Chrome normal (onde 1Password funciona)")
        print("2. 🌐 Vá para: https://trc-techresource.mastercard.com")
        print("3. 🍪 Feche modal de cookies")
        print("4. 🌐 Feche seletor de idioma")
        print("5. 👆 Clique no campo 'ID do utilizador'")
        print("6. 🔑 AGORA deve aparecer o ícone do 1Password!")
        print("7. 🖱️ Use 1Password para fazer login")
        print("8. 📱 Complete MFA se necessário")
        print("9. ⌨️ Pressione Enter aqui quando estiver LOGADO")
        print("="*80)
        print("💡 Use SEU Chrome normal, não uma nova janela!")
        print()
        
        input("⏳ Pressione Enter quando login estiver COMPLETO...")
        
        # Confirmação dupla
        confirm = input("✅ Tem certeza que está logado? (s/n): ").lower()
        
        if confirm == 's':
            logger.info("✅ Login confirmado!")
            return True
        else:
            logger.warning("⚠️ Login não confirmado")
            retry = input("❓ Quer tentar novamente? (s/n): ").lower()
            if retry == 's':
                return self.instruct_manual_login()
            return False
    
    def start_automation_for_collection(self):
        """Inicia automação apenas para coleta"""
        logger.info("🤖 Iniciando automação para coleta...")
        
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
            logger.info("✅ Chrome para coleta iniciado!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro iniciando automação: {e}")
            return False
    
    def navigate_assuming_login(self):
        """Navega assumindo que login já foi feito"""
        logger.info("🌐 Navegando para coleta...")
        
        try:
            self.driver.get("https://trc-techresource.mastercard.com")
            time.sleep(8)
            
            current_url = self.driver.current_url
            logger.info(f"📍 URL: {current_url}")
            
            # Se ainda na página de login
            if "sign-in" in current_url.lower():
                logger.warning("⚠️ Esta janela ainda precisa de login")
                
                print("\n" + "="*70)
                print("🔑 COMPLETE LOGIN NESTA JANELA TAMBÉM")
                print("="*70) 
                print("Esta é uma janela nova, precisa fazer login aqui também")
                print("Use 1Password normalmente")
                print("="*70)
                
                input("⏳ Pressione Enter quando fizer login nesta janela...")
                
                time.sleep(3)
                current_url = self.driver.current_url
                
                if "sign-in" in current_url.lower():
                    logger.error("❌ Login não detectado nesta janela")
                    return False
            
            logger.info("✅ Pronto para coletar PDFs!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro navegando: {e}")
            return False
    
    def collect_pdfs_automatically(self):
        """Coleta PDFs automaticamente"""
        logger.info("🤖 Coletando PDFs automaticamente...")
        
        try:
            time.sleep(5)
            
            # Procura PDFs com vários seletores
            pdf_selectors = [
                "a[href$='.pdf']",
                "a[href*='pdf']",
                "a[href*='PDF']",
                "a[title*='PDF']", 
                "a[title*='pdf']",
                "*[onclick*='pdf']",
                "*[onclick*='PDF']"
            ]
            
            found_pdfs = []
            
            logger.info("🔍 Procurando PDFs na página...")
            
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
                                logger.info(f"📄 PDF encontrado: {pdf_info['text']}")
                except:
                    continue
            
            # Procura também seções que podem ter PDFs
            self.search_for_document_sections()
            
            if found_pdfs:
                logger.info(f"✅ Total: {len(found_pdfs)} PDFs encontrados!")
                self.handle_pdf_downloads(found_pdfs)
            else:
                logger.info("⚠️ Nenhum PDF encontrado na página atual")
                self.suggest_manual_exploration()
                
        except Exception as e:
            logger.error(f"❌ Erro na coleta: {e}")
    
    def search_for_document_sections(self):
        """Procura seções que podem conter documentos"""
        logger.info("📂 Procurando seções de documentos...")
        
        section_keywords = [
            "documentation", "resources", "guides", "downloads",
            "developer", "technical", "api", "specs", "manual"
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
                        logger.info(f"�� Seção interessante: {text} -> {href}")
                        
            except:
                continue
    
    def handle_pdf_downloads(self, pdf_list):
        """Lida com downloads de PDFs"""
        print("\n" + "="*80)
        print("📄 PDFs ENCONTRADOS AUTOMATICAMENTE")
        print("="*80)
        for i, pdf in enumerate(pdf_list, 1):
            print(f"{i:2d}. {pdf['text']}")
            if pdf['href']:
                print(f"     URL: {pdf['href']}")
        print("="*80)
        
        choice = input("\n💾 (t)odos, (s)eletivos, ou (m)anual? [t/s/m]: ").lower()
        
        if choice == 't':
            self.download_all_pdfs(pdf_list)
        elif choice == 's':
            self.selective_download(pdf_list)
        else:
            self.manual_exploration_mode()
    
    def download_all_pdfs(self, pdf_list):
        """Baixa todos os PDFs"""
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
                time.sleep(3)
                
            except Exception as e:
                logger.warning(f"⚠️ Erro baixando {pdf['text']}: {e}")
        
        logger.info(f"✅ {success_count}/{len(pdf_list)} PDFs baixados!")
        logger.info(f"📁 Local: {self.download_dir}")
    
    def selective_download(self, pdf_list):
        """Download seletivo"""
        print("\n🎯 Digite os números dos PDFs para baixar (ex: 1,3,5):")
        selection = input("Números: ").strip()
        
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected_pdfs = [pdf_list[i] for i in indices if 0 <= i < len(pdf_list)]
            
            if selected_pdfs:
                self.download_all_pdfs(selected_pdfs)
            else:
                logger.warning("⚠️ Seleção inválida")
        except:
            logger.error("❌ Formato inválido")
    
    def suggest_manual_exploration(self):
        """Sugere exploração manual"""
        print("\n" + "="*80)
        print("🔍 SUGESTÕES PARA ENCONTRAR PDFs")
        print("="*80)
        print("Procure por estas seções no site:")
        print("• Documentation")
        print("• Developer Resources") 
        print("• Technical Guides")
        print("• Downloads")
        print("• API Documentation")
        print("• Integration Guides")
        print("="*80)
        
        self.manual_exploration_mode()
    
    def manual_exploration_mode(self):
        """Modo exploração manual"""
        print("\n🔍 Navegador ficará aberto para exploração manual")
        print("Explore o site e baixe PDFs manualmente")
        input("Pressione Enter quando terminar...")
    
    def run_simple_hybrid(self):
        """Executa processo híbrido simples"""
        logger.info("🚀 Iniciando processo híbrido simples...")
        
        try:
            # 1. Instrui login manual
            if not self.instruct_manual_login():
                logger.error("❌ Login manual não confirmado")
                return False
            
            # 2. Inicia automação
            if not self.start_automation_for_collection():
                logger.error("❌ Falha ao iniciar automação")
                return False
            
            # 3. Navega para coleta
            if not self.navigate_assuming_login():
                logger.error("❌ Falha na navegação")
                return False
            
            # 4. Coleta automática
            self.collect_pdfs_automatically()
            
            logger.info("🎉 Processo híbrido concluído!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no processo: {e}")
            return False
    
    def close(self):
        try:
            if hasattr(self, 'driver'):
                input("\n🔒 Pressione Enter para fechar automação...")
                self.driver.quit()
                logger.info("✅ Automação fechada")
        except:
            pass

def main():
    logger.info("🚀 Mastercard Bot - Híbrido Simples")
    
    bot = MastercardSimpleHybridBot()
    
    try:
        success = bot.run_simple_hybrid()
        
        if success:
            logger.info("🎉 MISSÃO CUMPRIDA!")
        else:
            logger.error("❌ Processo não concluído")
            
    except KeyboardInterrupt:
        logger.info("⏹️ Interrompido")
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()
