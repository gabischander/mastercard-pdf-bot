#!/usr/bin/env python3
"""
Mastercard Real-time Monitor
Monitora downloads em tempo real enquanto o usuário clica
"""

import time
import zipfile
import shutil
import os
from datetime import datetime, timedelta
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class RealtimeMonitor:
    def __init__(self):
        self.download_dir = Path("downloads_realtime")
        self.pdf_dir = Path("pdfs_realtime")
        self.setup_directories()
        self.driver = None
        
    def setup_directories(self):
        """Prepara diretórios"""
        self.download_dir.mkdir(exist_ok=True)
        self.pdf_dir.mkdir(exist_ok=True)
        
        print(f"✅ Pasta de downloads: {self.download_dir.absolute()}")
        print(f"✅ Pasta de PDFs: {self.pdf_dir.absolute()}")
        
    def setup_chrome(self):
        """Configura Chrome para downloads"""
        chrome_options = Options()
        
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
        
        print("🌐 Abrindo Mastercard Connect...")
        self.driver.get("https://mastercardconnect.com")
        
        print("\n" + "="*60)
        print("🎯 MONITOR EM TEMPO REAL ATIVO!")
        print("="*60)
        print("1. 🔑 Faça login e vá para Announcements")
        print("2. 👀 Procure documentos com Publication Date: 25 Jun - 01 Jul 2025")
        print("3. 🖱️ Clique nos ícones de download")
        print("4. 📺 Deixe esta janela aberta - mostrarei os downloads detectados")
        print("="*60)
        
        input("\nPressione ENTER quando estiver pronto para começar o monitoramento...")
        
    def monitor_downloads_realtime(self):
        """Monitora downloads em tempo real"""
        print(f"\n👀 MONITORAMENTO ATIVO...")
        print(f"📁 Pasta: {self.download_dir}")
        print("🖱️ Clique nos ícones de download - detectarei automaticamente!")
        print("⌨️ Digite Ctrl+C quando terminar\n")
        
        initial_files = set(f.name for f in self.download_dir.glob("*") if f.is_file())
        detected_downloads = []
        last_check_time = time.time()
        
        try:
            while True:
                # Verifica novos arquivos
                current_files = set(f.name for f in self.download_dir.glob("*") if f.is_file())
                new_files = current_files - initial_files
                
                # Verifica se há arquivos novos ou modificados recentemente
                recent_files = []
                for file_path in self.download_dir.glob("*"):
                    if file_path.is_file():
                        file_time = file_path.stat().st_mtime
                        if file_time > last_check_time - 5:  # Últimos 5 segundos
                            if file_path.name not in [d['file'].name for d in detected_downloads]:
                                recent_files.append(file_path)
                
                # Processa novos downloads
                for file_path in recent_files:
                    if not file_path.name.endswith(('.crdownload', '.tmp', '.part')):
                        detected_downloads.append({
                            'file': file_path,
                            'time': datetime.now(),
                            'size': file_path.stat().st_size
                        })
                        
                        size_mb = file_path.stat().st_size / (1024 * 1024)
                        time_str = datetime.now().strftime('%H:%M:%S')
                        
                        print(f"🎉 DOWNLOAD {len(detected_downloads)} DETECTADO!")
                        print(f"   📁 {file_path.name}")
                        print(f"   📊 {size_mb:.2f} MB")
                        print(f"   ⏰ {time_str}")
                        print("   🖱️ Continue clicando para mais downloads...\n")
                
                # Atualiza arquivos iniciais
                initial_files = current_files
                last_check_time = time.time()
                
                # Pausa curta
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n⏹️ Monitoramento finalizado.")
            print(f"📊 Total de downloads detectados: {len(detected_downloads)}")
            
        return detected_downloads
        
    def check_other_download_locations(self):
        """Verifica outras possíveis localizações de downloads"""
        print(f"\n🔍 VERIFICANDO OUTRAS PASTAS DE DOWNLOAD...")
        
        # Possíveis localizações de downloads
        possible_locations = [
            Path.home() / "Downloads",
            Path.home() / "Desktop", 
            Path("/Users/gabrielaschander/Downloads"),
            Path("/Users/gabrielaschander/Desktop"),
            Path("/tmp"),
        ]
        
        found_files = []
        
        for location in possible_locations:
            if location.exists():
                print(f"📂 Verificando: {location}")
                
                # Procura por arquivos recentes (últimos 30 minutos)
                cutoff_time = time.time() - (30 * 60)
                
                try:
                    for file_path in location.glob("*"):
                        if file_path.is_file():
                            # Verifica se é arquivo relacionado ao Mastercard
                            if any(keyword in file_path.name.lower() for keyword in ['mastercard', 'glb', 'lac', '.zip', '.pdf']):
                                if file_path.stat().st_mtime > cutoff_time:
                                    found_files.append(file_path)
                                    size_mb = file_path.stat().st_size / (1024 * 1024)
                                    print(f"   📄 Encontrado: {file_path.name} ({size_mb:.2f} MB)")
                                    
                except PermissionError:
                    print(f"   ❌ Sem permissão para acessar")
                    
        if found_files:
            print(f"\n📋 Arquivos relacionados encontrados: {len(found_files)}")
            
            copy_choice = input("🔄 Quer copiar estes arquivos para nossa pasta? (s/n): ").strip().lower()
            
            if copy_choice in ['s', 'sim', 'yes', 'y']:
                copied_files = []
                for file_path in found_files:
                    try:
                        dest_path = self.download_dir / file_path.name
                        shutil.copy2(file_path, dest_path)
                        copied_files.append(dest_path)
                        print(f"   ✅ Copiado: {file_path.name}")
                    except Exception as e:
                        print(f"   ❌ Erro ao copiar {file_path.name}: {e}")
                        
                return copied_files
        else:
            print("   ❌ Nenhum arquivo relacionado encontrado")
            
        return []
        
    def extract_all_pdfs(self, downloaded_files):
        """Extrai PDFs de todos os arquivos"""
        if not downloaded_files:
            return []
            
        print(f"\n📦 PROCESSANDO {len(downloaded_files)} ARQUIVOS...")
        
        extracted_pdfs = []
        
        for i, file_info in enumerate(downloaded_files):
            if isinstance(file_info, dict):
                file_path = file_info['file']
            else:
                file_path = file_info
                
            try:
                print(f"\n📂 Arquivo {i+1}: {file_path.name}")
                
                if file_path.suffix.lower() == '.zip':
                    extract_dir = self.pdf_dir / f"zip_{i+1}_{file_path.stem}"
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
        """Executa monitor em tempo real"""
        print("⏱️ MASTERCARD REALTIME MONITOR")
        print("=" * 60)
        print("📅 Período: 25 Jun - 01 Jul 2025")
        print("=" * 60)
        
        try:
            # Configura Chrome
            self.setup_chrome()
            
            # Monitora em tempo real
            detected_downloads = self.monitor_downloads_realtime()
            
            # Verifica outras localizações
            other_files = self.check_other_download_locations()
            
            # Combina todos os arquivos
            all_files = detected_downloads + other_files
            
            if not all_files:
                print("\n😔 Nenhum download detectado")
                print("\n💡 POSSÍVEIS PROBLEMAS:")
                print("   • Os ícones podem não estar funcionando")
                print("   • Downloads foram para pasta diferente")
                print("   • Necessário login/autenticação adicional")
                print("   • Site pode estar bloqueando downloads automáticos")
                return False
                
            # Processa arquivos
            extracted_pdfs = self.extract_all_pdfs(all_files)
            
            # Relatório final
            print("\n" + "="*60)
            print("🎉 RELATÓRIO FINAL!")
            print(f"📥 Downloads detectados: {len(detected_downloads)}")
            print(f"📁 Arquivos de outras pastas: {len(other_files)}")
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
    monitor = RealtimeMonitor()
    
    try:
        success = monitor.run()
        
        if success:
            print("\n🎉 DOWNLOADS PROCESSADOS!")
        else:
            print("\n🔧 Vamos tentar outras abordagens se necessário...")
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo interrompido")

if __name__ == "__main__":
    main()
