#!/usr/bin/env python3
"""
Mastercard Simple Monitor
Apenas monitora downloads sem interferir na página
"""

import time
import zipfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class SimpleMonitor:
    def __init__(self):
        self.download_dir = Path("downloads_simple")
        self.pdf_dir = Path("pdfs_simple") 
        self.setup_directories()
        self.driver = None
        
    def setup_directories(self):
        """Prepara diretórios"""
        self.download_dir.mkdir(exist_ok=True)
        self.pdf_dir.mkdir(exist_ok=True)
        
        print(f"✅ Pasta de downloads: {self.download_dir.absolute()}")
        print(f"✅ Pasta de PDFs: {self.pdf_dir.absolute()}")
        
    def setup_chrome(self):
        """Configura Chrome APENAS para downloads - sem interferir na página"""
        chrome_options = Options()
        
        # Configurações de download
        download_path = str(self.download_dir.absolute())
        prefs = {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Apenas abre a página - NÃO FAZ MAIS NADA
        print("🌐 Abrindo Mastercard Connect...")
        self.driver.get("https://mastercardconnect.com")
        
        print("\n" + "="*60)
        print("🎯 INSTRUÇÕES SIMPLES:")
        print("1. 🔑 Faça login no site")
        print("2. 🏢 Vá para Technical Resource Center > Announcements") 
        print("3. 👀 Encontre documentos com Publication Date entre 25 Jun - 01 Jul 2025")
        print("4. 🖱️ Clique normalmente nos ícones de download (seta para baixo)")
        print("5. 📁 Os arquivos serão baixados para a pasta configurada")
        print("="*60)
        
        input("\nPressione ENTER quando tiver terminado de baixar os arquivos...")
        
    def check_downloads(self):
        """Verifica arquivos baixados"""
        files = list(self.download_dir.glob("*"))
        downloaded_files = [f for f in files if f.is_file()]
        
        print(f"\n📁 Arquivos encontrados na pasta de downloads: {len(downloaded_files)}")
        
        if downloaded_files:
            print("📋 Lista de arquivos:")
            for i, file in enumerate(downloaded_files):
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"   {i+1}. {file.name} ({size_mb:.2f} MB)")
                
        return downloaded_files
        
    def extract_pdfs(self, downloaded_files):
        """Extrai PDFs dos arquivos"""
        if not downloaded_files:
            return []
            
        print(f"\n📦 Processando {len(downloaded_files)} arquivos...")
        
        extracted_pdfs = []
        
        for i, file_path in enumerate(downloaded_files):
            try:
                print(f"\n📂 Arquivo {i+1}: {file_path.name}")
                
                if file_path.suffix.lower() == '.zip':
                    # Extrai ZIP
                    extract_dir = self.pdf_dir / f"extracted_{file_path.stem}"
                    extract_dir.mkdir(exist_ok=True)
                    
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        pdf_files = [f for f in zip_ref.namelist() if f.lower().endswith('.pdf')]
                        
                        print(f"   📄 PDFs no ZIP: {len(pdf_files)}")
                        
                        for pdf_file in pdf_files:
                            zip_ref.extract(pdf_file, extract_dir)
                            extracted_pdf = extract_dir / pdf_file
                            extracted_pdfs.append(extracted_pdf)
                            print(f"      ✅ {pdf_file}")
                            
                elif file_path.suffix.lower() == '.pdf':
                    # Copia PDF
                    pdf_dest = self.pdf_dir / file_path.name
                    shutil.copy2(file_path, pdf_dest)
                    extracted_pdfs.append(pdf_dest)
                    print(f"   ✅ PDF copiado")
                    
                else:
                    print(f"   ⚠️ Tipo não suportado: {file_path.suffix}")
                    
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                continue
                
        return extracted_pdfs
        
    def run(self):
        """Executa monitor simples"""
        print("🔍 MASTERCARD SIMPLE MONITOR")
        print("=" * 50)
        print("📅 Período: 25 Jun - 01 Jul 2025")
        print("=" * 50)
        
        try:
            # Apenas configura Chrome e abre página
            self.setup_chrome()
            
            # Verifica downloads
            downloaded_files = self.check_downloads()
            
            if not downloaded_files:
                print("\n😔 Nenhum arquivo encontrado na pasta de downloads")
                print(f"🔍 Verifique se os downloads foram para: {self.download_dir.absolute()}")
                return False
                
            # Processa arquivos
            extracted_pdfs = self.extract_pdfs(downloaded_files)
            
            # Relatório
            print("\n" + "="*50)
            print("🎉 RESULTADO FINAL!")
            print(f"📥 Arquivos baixados: {len(downloaded_files)}")
            print(f"📄 PDFs extraídos: {len(extracted_pdfs)}")
            
            if extracted_pdfs:
                print(f"\n📁 PDFs ORGANIZADOS EM: {self.pdf_dir.absolute()}")
                for pdf in extracted_pdfs:
                    print(f"  • {pdf.name}")
                    
            return len(extracted_pdfs) > 0
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
            
        finally:
            if self.driver:
                input("\nPressione ENTER para fechar o navegador...")
                self.driver.quit()

def main():
    monitor = SimpleMonitor()
    
    try:
        success = monitor.run()
        
        if success:
            print("\n🎉 DOWNLOADS PROCESSADOS COM SUCESSO!")
        else:
            print("\n💡 Dica: Certifique-se de clicar nos ícones de download na página")
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo interrompido")

if __name__ == "__main__":
    main()
