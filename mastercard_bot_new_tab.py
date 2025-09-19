#!/usr/bin/env python3
"""
Mastercard PDF Bot - Abre nova aba no seu Chrome
"""
import os
import time
import logging
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class MastercardNewTabBot:
    def __init__(self):
        self.download_dir = Path("mastercard_pdfs")
        self.download_dir.mkdir(exist_ok=True)
        logger.info("✅ Bot Nova Aba iniciado")
    
    def open_mastercard_in_new_tab(self):
        """Abre Mastercard em nova aba do seu Chrome"""
        logger.info("🌐 Abrindo Mastercard em nova aba...")
        
        try:
            # Comando para abrir nova aba no Chrome existente
            url = "https://trc-techresource.mastercard.com"
            cmd = ["open", "-a", "Google Chrome", url]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Nova aba aberta no Chrome!")
                logger.info(f"🔗 URL: {url}")
                return True
            else:
                logger.error(f"❌ Erro abrindo Chrome: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return False
    
    def wait_and_guide_user(self):
        """Guia usuário através do processo"""
        logger.info("👨‍🏫 Guiando usuário...")
        
        print("\n" + "="*80)
        print("🔑 NOVA ABA ABERTA NO SEU CHROME!")
        print("="*80)
        print("1. 🖥️ Vá para a nova aba que abriu")
        print("2. ⏳ Aguarde página carregar completamente")
        print("3. 🍪 Feche o modal de cookies (se aparecer)")
        print("4. 🌐 Feche seletor de idioma (se aparecer)")
        print("5. 👆 Clique no campo 'ID do utilizador'")
        print("6. 🔑 AGORA você deve ver o ícone do 1Password!")
        print("7. 🖱️ Clique no ícone do 1Password ou use Cmd+\\")
        print("8. 🔐 Selecione suas credenciais Mastercard")
        print("9. 🚀 Faça login normalmente")
        print("10. 📱 Complete MFA se necessário")
        print("="*80)
        print("💡 Como está usando SEU Chrome, 1Password deve funcionar normal!")
        print()
        
        # Aguarda confirmação
        input("⏳ Pressione Enter quando login estiver completo...")
        
        # Pede confirmação
        login_ok = input("✅ Login foi realizado com sucesso? (s/n): ").lower()
        
        return login_ok == 's'
    
    def guide_pdf_collection(self):
        """Guia coleta de PDFs"""
        logger.info("📄 Orientando coleta de PDFs...")
        
        print("\n" + "="*80)
        print("📄 COLETANDO PDFs")
        print("="*80)
        print("Agora que você está logado:")
        print()
        print("1. 🔍 Navegue pelo site procurando PDFs")
        print("2. 📄 Procure por:")
        print("   • Links de documentação")
        print("   • Guias técnicos")
        print("   • Especificações")
        print("   • Recursos para desenvolvedores")
        print("3. 💾 Clique nos PDFs para baixar")
        print("4. 📁 Downloads irão para: Downloads/")
        print()
        print("💡 Dicas para encontrar PDFs:")
        print("• Procure seções como 'Resources', 'Documentation'")
        print("• Procure links que terminam com '.pdf'")
        print("• Verifique menus e submenus")
        print("="*80)
        
        # Pergunta se quer ajuda para procurar
        help_search = input("\n🤖 Quer que eu te ajude a procurar PDFs automaticamente? (s/n): ").lower()
        
        if help_search == 's':
            self.suggest_pdf_locations()
        
        input("\n✅ Pressione Enter quando terminar de coletar PDFs...")
    
    def suggest_pdf_locations(self):
        """Sugere locais onde procurar PDFs"""
        logger.info("🎯 Sugerindo locais para PDFs...")
        
        print("\n" + "="*70)
        print("🎯 LOCAIS SUGERIDOS PARA PDFs")
        print("="*70)
        print()
        print("🔍 Procure nestas seções/URLs:")
        print("• Developer Resources")
        print("• Technical Documentation") 
        print("• API Guides")
        print("• Integration Guides")
        print("• Security Guidelines")
        print("• Testing Resources")
        print("• Certification Documents")
        print()
        print("🔗 URLs típicas para tentar:")
        print("• .../documentation")
        print("• .../resources")
        print("• .../developer")
        print("• .../guides")
        print("• .../downloads")
        print("="*70)
    
    def run_guided_session(self):
        """Executa sessão guiada"""
        logger.info("🚀 Iniciando sessão guiada...")
        
        try:
            # 1. Abre nova aba
            if not self.open_mastercard_in_new_tab():
                logger.error("❌ Não conseguiu abrir nova aba")
                return False
            
            # Aguarda um pouco para aba carregar
            time.sleep(3)
            
            # 2. Guia login
            login_success = self.wait_and_guide_user()
            
            if login_success:
                logger.info("🎉 LOGIN CONFIRMADO!")
                
                # 3. Guia coleta de PDFs
                self.guide_pdf_collection()
                
                logger.info("✅ Sessão guiada concluída!")
                return True
            else:
                logger.error("❌ Login não foi realizado")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro na sessão: {e}")
            return False

def main():
    logger.info("🚀 Mastercard Bot - Nova Aba + 1Password")
    
    bot = MastercardNewTabBot()
    
    try:
        success = bot.run_guided_session()
        
        if success:
            logger.info("🎉 SUCESSO! PDFs coletados via nova aba")
        else:
            logger.error("❌ Sessão não foi concluída")
            
    except KeyboardInterrupt:
        logger.info("⏹️ Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
