#!/usr/bin/env python3
"""
Mastercard Manual Monitor
Monitora downloads enquanto o usuário clica manualmente nos ícones
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

class ManualMonitorDownloader:
    def __init__(self):
        self.download_dir = Path("downloads_manual_monitor")
        self.pdf_dir = Path("pdfs_manual_monitor")
        self.setup_directories()
        self.driver = None
        self.initial_files = set()
        
    def setup_directories(self):
        """Prepara diretórios"""
        self.download_dir.mkdir(exist_ok=True)
        self.pdf_dir.mkdir(exist_ok=True)
        
        # Limpa arquivos anteriores
        for file in self.download_dir.glob("*"):
            if file.is_file():
                file.unlink()
        for file in self.pdf_dir.glob("*"):
            if file.is_file():
                file.unlink()
                
        print(f"✅ Diretórios preparados: {self.download_dir}, {self.pdf_dir}")
        
    def get_target_date_range(self):
        """Calcula período"""
        today = datetime.now()
        
        days_since_wednesday = (today.weekday() - 2) % 7
        if days_since_wednesday == 0 and today.weekday() == 2:
            last_wednesday = today - timedelta(days=7)
        else:
            last_wednesday = today - timedelta(days=days_since_wednesday)
            
        if last_wednesday > today:
            last_wednesday = last_wednesday - timedelta(days=7)
            
        print(f"🗓️ Hoje: {today.strftime('%d %b %Y (%A)')}")
        print(f"🎯 Período: {last_wednesday.strftime('%d %b %Y')} até {today.strftime('%d %b %Y')}")
        
        return last_wednesday, today
        
    def setup_chrome(self):
        """Configura Chrome"""
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
        
    def navigate_to_announcements(self):
        """Navega para announcements"""
        print("\n🌐 Abrindo mastercardconnect.com...")
        self.driver.get("https://mastercardconnect.com")
        time.sleep(3)
        
        range_start, range_end = self.get_target_date_range()
        
        print(f"\n🎯 DOCUMENTOS A BAIXAR: {range_start.strftime('%d %b')} - {range_end.strftime('%d %b %Y')}")
        print("="*60)
        print("1. 🔑 Faça login")
        print("2. 🏢 Vá para Technical Resource Center")  
        print("3. 📢 Clique em Announcements")
        print("4. 👀 Aguarde ver os documentos")
        print("="*60)
        
        input("Pressione ENTER quando estiver vendo os documentos...")
        
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            print("✅ Usando última aba")
            
        time.sleep(5)
        
        # Registra arquivos iniciais
        self.initial_files = set(f.name for f in self.download_dir.glob("*") if f.is_file())
        print(f"📁 Arquivos iniciais na pasta: {len(self.initial_files)}")
        
    def monitor_downloads(self):
        """Monitora downloads em tempo real"""
        print(f"\n👀 MONITOR DE DOWNLOADS ATIVO")
        print("="*60)
        print("🎯 INSTRUÇÕES:")
        print("1. 👀 Olhe na página e identifique os documentos com Publication Date no período")
        print("2. 🖱️ Clique nos ícones de download (seta para baixo) de cada documento")
        print("3. ⏳ O script detectará automaticamente quando os downloads começarem")
        print("4. ⌨️ Digite 'parar' quando terminar ou 'status' para ver progresso")
        print("="*60)
        
        downloaded_files = []
        download_count = 0
        
        print(f"\n📥 MONITORAMENTO INICIADO... (pasta: {self.download_dir})")
        print("💡 Dica: Clique nos ícones de seta para baixo no canto direito dos documentos")
        
        last_file_count = len(self.initial_files)
        
        while True:
            try:
                # Verifica novos arquivos
                current_files = set(f.name for f in self.download_dir.glob("*") if f.is_file())
                new_files = current_files - self.initial_files
                
                if len(current_files) > last_file_count:
                    # Novo arquivo detectado
                    newest_files = sorted(
                        [f for f in self.download_dir.glob("*") if f.is_file() and f.name in new_files],
                        key=lambda x: x.stat().st_mtime,
                        reverse=True
                    )
                    
                    for new_file in newest_files:
                        if new_file.name not in [d['file'].name for d in downloaded_files]:
                            download_count += 1
                            
                            downloaded_files.append({
                                'file': new_file,
                                'download_time': datetime.now(),
                                'size': new_file.stat().st_size
                            })
                            
                            size_mb = new_file.stat().st_size / (1024 * 1024)
                            print(f"\n🎉 DOWNLOAD {download_count} DETECTADO!")
                            print(f"   📁 Arquivo: {new_file.name}")
                            print(f"   📊 Tamanho: {size_mb:.2f} MB")
                            print(f"   ⏰ Hora: {datetime.now().strftime('%H:%M:%S')}")
                            
                    last_file_count = len(current_files)
                
                # Verifica comando do usuário (não bloqueante)
                print("Digite 'parar' para finalizar, 'status' para status, ou apenas continue clicando: ", end="", flush=True)
                
                # Aguarda um pouco antes de verificar novamente
                time.sleep(2)
                
                # Simulação de input não bloqueante (simplificado)
                # Em uma implementação real, usaria threading ou select
                
                # Pergunta ocasionalmente se quer continuar
                if download_count > 0 and download_count % 3 == 0:
                    response = input(f"\n👍 {download_count} downloads detectados. Continuar? (s/n/status): ").strip().lower()
                    
                    if response in ['n', 'não', 'nao', 'parar', 'stop']:
                        break
                    elif response == 'status':
                        self.show_status(downloaded_files)
                        
            except KeyboardInterrupt:
                print("\n\n⏹️ Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                print(f"\n❌ Erro no monitoramento: {e}")
                continue
                
        return downloaded_files
        
    def show_status(self, downloaded_files):
        """Mostra status atual"""
        print(f"\n📊 STATUS ATUAL:")
        print(f"   📥 Downloads detectados: {len(downloaded_files)}")
        
        if downloaded_files:
            print(f"   📁 Arquivos:")
            for i, file_info in enumerate(downloaded_files):
                size_mb = file_info['size'] / (1024 * 1024)
                time_str = file_info['download_time'].strftime('%H:%M:%S')
                print(f"      {i+1}. {file_info['file'].name} ({size_mb:.2f} MB) - {time_str}")
                
    def extract_and_organize_pdfs(self, downloaded_files):
        """Extrai e organiza PDFs"""
        if not downloaded_files:
            print("\n📂 Nenhum arquivo para processar")
            return []
            
        print(f"\n📂 Processando {len(downloaded_files)} arquivos...")
        
        extracted_pdfs = []
        
        for i, file_info in enumerate(downloaded_files):
            file_path = file_info['file']
            
            try:
                print(f"\n📦 Processando {i+1}/{len(downloaded_files)}: {file_path.name}")
                
                if file_path.suffix.lower() == '.zip':
                    # Extrai ZIP
                    extract_dir = self.pdf_dir / f"zip_{i+1}_{file_path.stem}"
                    extract_dir.mkdir(exist_ok=True)
                    
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_members = zip_ref.namelist()
                        pdf_members = [m for m in zip_members if m.lower().endswith('.pdf')]
                        
                        print(f"   📄 PDFs no ZIP: {len(pdf_members)}")
                        
                        for member in pdf_members:
                            zip_ref.extract(member, extract_dir)
                            extracted_pdf = extract_dir / member
                            
                            extracted_pdfs.append({
                                'pdf_path': extracted_pdf,
                                'original_zip': file_path.name,
                                'download_time': file_info['download_time']
                            })
                            
                            print(f"      ✅ {member}")
                            
                elif file_path.suffix.lower() == '.pdf':
                    # Copia PDF diretamente
                    pdf_dest = self.pdf_dir / file_path.name
                    shutil.copy2(file_path, pdf_dest)
                    
                    extracted_pdfs.append({
                        'pdf_path': pdf_dest,
                        'original_zip': None,
                        'download_time': file_info['download_time']
                    })
                    
                    print(f"   ✅ PDF copiado: {file_path.name}")
                    
                else:
                    print(f"   ⚠️ Tipo de arquivo não suportado: {file_path.suffix}")
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar {file_path}: {e}")
                continue
                
        return extracted_pdfs
        
    def interactive_session(self):
        """Sessão interativa para continuar downloads"""
        while True:
            response = input("\n🎯 Quer fazer mais downloads? (s/n): ").strip().lower()
            
            if response in ['n', 'não', 'nao', 'parar', 'stop']:
                break
            elif response in ['s', 'sim', 'yes', 'y']:
                print("👍 Continue clicando nos ícones de download...")
                
                # Monitora por mais alguns minutos
                additional_downloads = []
                start_time = time.time()
                
                while time.time() - start_time < 120:  # 2 minutos
                    current_files = set(f.name for f in self.download_dir.glob("*") if f.is_file())
                    
                    # Verifica novos arquivos
                    for file in self.download_dir.glob("*"):
                        if file.is_file() and file.stat().st_mtime > start_time:
                            if file not in additional_downloads:
                                additional_downloads.append(file)
                                print(f"✅ Novo download: {file.name}")
                                
                    time.sleep(3)
                    
                    # Verifica se usuário quer parar
                    try:
                        # Implementação simplificada - na prática usaria threading
                        pass
                    except:
                        break
                        
                if additional_downloads:
                    print(f"📥 {len(additional_downloads)} downloads adicionais detectados")
                    
                return additional_downloads
            else:
                print("❓ Responda 's' para sim ou 'n' para não")
                
        return []
        
    def run(self):
        """Executa o monitor manual"""
        print("👁️ MASTERCARD MANUAL MONITOR")
        print("=" * 60)
        
        try:
            self.setup_chrome()
            self.navigate_to_announcements()
            
            # Monitora downloads manuais
            downloaded_files = self.monitor_downloads()
            
            if not downloaded_files:
                print("\n😔 Nenhum download foi detectado")
                
                # Oferece sessão interativa
                print("\n🤔 Quer tentar mais alguns downloads?")
                additional = self.interactive_session()
                
                if additional:
                    downloaded_files.extend([{'file': f, 'download_time': datetime.now(), 'size': f.stat().st_size} for f in additional])
                    
            if downloaded_files:
                # Processa arquivos
                extracted_pdfs = self.extract_and_organize_pdfs(downloaded_files)
                
                # Relatório final
                range_start, range_end = self.get_target_date_range()
                
                print("\n" + "="*60)
                print("🎉 RELATÓRIO FINAL!")
                print(f"📅 Período: {range_start.strftime('%d %b')} - {range_end.strftime('%d %b %Y')}")
                print(f"📥 Downloads detectados: {len(downloaded_files)}")
                print(f"📄 PDFs extraídos: {len(extracted_pdfs)}")
                
                if extracted_pdfs:
                    print(f"\n📁 PDFs ORGANIZADOS EM: {self.pdf_dir.absolute()}")
                    for pdf in extracted_pdfs:
                        zip_info = f" (de {pdf['original_zip']})" if pdf['original_zip'] else ""
                        time_str = pdf['download_time'].strftime('%H:%M:%S')
                        print(f"  • {pdf['pdf_path'].name}{zip_info} - {time_str}")
                        
                return len(extracted_pdfs) > 0
            else:
                return False
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
            
        finally:
            if self.driver:
                input("\nPressione ENTER para fechar o navegador...")
                self.driver.quit()

def main():
    monitor = ManualMonitorDownloader()
    
    try:
        success = monitor.run()
        
        if success:
            print("\n🎉 DOWNLOADS MONITORADOS COM SUCESSO!")
        else:
            print("\n😔 Nenhum download foi realizado")
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo interrompido")

if __name__ == "__main__":
    main()
