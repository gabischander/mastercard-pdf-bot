#!/usr/bin/env python3
"""
Mastercard Weekly PDF Collector
Coleta PDFs do Technical Resource Center > Announcements
Filtra por Publication Date da semana anterior
"""

import os
import time
import zipfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mastercard_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MastercardWeeklyCollector:
    def __init__(self):
        self.download_dir = Path("downloads")
        self.pdf_dir = Path("pdfs")
        self.setup_directories()
        self.driver = None
        
    def setup_directories(self):
        """Cria diretórios necessários"""
        self.download_dir.mkdir(exist_ok=True)
        self.pdf_dir.mkdir(exist_ok=True)
        logger.info(f"Diretórios configurados: {self.download_dir}, {self.pdf_dir}")
        
    def get_previous_week_dates(self):
        """Calcula as datas da semana anterior"""
        today = datetime.now()
        
        # Encontra a segunda-feira da semana anterior
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        
        # Semana anterior: segunda a domingo
        week_start = last_monday
        week_end = last_monday + timedelta(days=6)
        
        logger.info(f"Semana anterior: {week_start.strftime('%d %b %Y')} até {week_end.strftime('%d %b %Y')}")
        return week_start, week_end
        
    def setup_chrome(self):
        """Configura o Chrome para usar o perfil do usuário"""
        chrome_options = Options()
        
        # Diretório de download
        download_path = str(self.download_dir.absolute())
        prefs = {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Usar perfil do usuário (onde está o 1Password)
        user_data_dir = "/Users/gabrielaschander/Library/Application Support/Google/Chrome"
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--profile-directory=Default")
        
        # Outras configurações
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        
        try:
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Chrome driver inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar Chrome: {e}")
            # Fallback para Chrome padrão
            chrome_options = Options()
            chrome_options.add_experimental_option("prefs", prefs)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
    def login_to_mastercard(self):
        """Realiza login no site Mastercard"""
        logger.info("Iniciando processo de login...")
        
        try:
            # Navega para a página de login
            self.driver.get("https://mastercardconnect.com")
            logger.info("Navegando para mastercardconnect.com")
            
            # Aguarda a página carregar
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Aguarda 3 segundos para tudo carregar
            time.sleep(3)
            
            # Procura e remove overlays/modals que podem estar bloqueando
            self.remove_overlays()
            
            # Procura pelo campo de username/email
            username_selectors = [
                'input[name="userId"]',
                'input[name="username"]', 
                'input[name="email"]',
                'input[type="email"]',
                '#userId',
                '#username',
                '#email'
            ]
            
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Campo de username encontrado com seletor: {selector}")
                    break
                except:
                    continue
                    
            if not username_field:
                logger.error("Campo de username não encontrado")
                return False
                
            # Procura pelo campo de password
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                '#password'
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"Campo de password encontrado com seletor: {selector}")
                    break
                except:
                    continue
                    
            if not password_field:
                logger.error("Campo de password não encontrado")
                return False
            
            # Preenche as credenciais
            logger.info("Preenchendo credenciais...")
            username_field.clear()
            username_field.send_keys("gabriela.braga@cloudwalk.io")
            
            password_field.clear()
            password_field.send_keys("Medemotivos!")
            
            # Procura pelo botão de login
            login_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:contains("Sign")',
                'button:contains("Login")',
                'button:contains("Iniciar")',
                '.login-button',
                '#loginButton'
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    if ':contains(' in selector:
                        # Para seletores com contains, usa XPath
                        xpath_selector = f"//button[contains(text(), '{selector.split(':contains(')[1].split(')')')[0].strip('\"')}')]"
                        login_button = self.driver.find_element(By.XPATH, xpath_selector)
                    else:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"Botão de login encontrado com seletor: {selector}")
                    break
                except:
                    continue
                    
            if not login_button:
                logger.error("Botão de login não encontrado")
                return False
                
            # Clica no botão de login
            logger.info("Clicando no botão de login...")
            self.driver.execute_script("arguments[0].click();", login_button)
            
            # Aguarda redirecionamento ou página de dashboard
            time.sleep(5)
            
            logger.info("Login executado. Aguardando confirmação...")
            return True
            
        except Exception as e:
            logger.error(f"Erro durante login: {e}")
            return False
            
    def remove_overlays(self):
        """Remove overlays e modals que podem bloquear interações"""
        overlay_selectors = [
            '.onetrust-pc-dark-filter',
            '.onetrust-banner-sdk',
            '.ot-fade-in',
            '[id*="onetrust"]',
            '.modal-backdrop',
            '.overlay',
            '.popup'
        ]
        
        for selector in overlay_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    self.driver.execute_script("arguments[0].remove();", element)
                    logger.info(f"Overlay removido: {selector}")
            except:
                pass
                
    def navigate_to_announcements(self):
        """Navega para Technical Resource Center > Announcements"""
        logger.info("Navegando para Technical Resource Center > Announcements...")
        
        try:
            # Aguarda a página carregar após login
            time.sleep(3)
            
            # Procura por links que levam ao Technical Resource Center
            trc_selectors = [
                'a[href*="technical"]',
                'a[href*="resource"]',
                'a[href*="center"]',
                'a:contains("Technical")',
                'a:contains("Resource")',
                'a:contains("Center")'
            ]
            
            trc_link = None
            for selector in trc_selectors:
                try:
                    if ':contains(' in selector:
                        text = selector.split(':contains(')[1].split(')')')[0].strip('\"')
                        xpath_selector = f"//a[contains(text(), '{text}') or contains(@title, '{text}')]"
                        trc_link = self.driver.find_element(By.XPATH, xpath_selector)
                    else:
                        trc_link = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"Link TRC encontrado: {selector}")
                    break
                except:
                    continue
                    
            if trc_link:
                logger.info("Clicando no Technical Resource Center...")
                self.driver.execute_script("arguments[0].click();", trc_link)
                time.sleep(3)
            else:
                # Tenta acessar diretamente se conhecemos a URL
                logger.info("Tentando acesso direto ao TRC...")
                possible_urls = [
                    "https://mastercardconnect.com/technical-resource-center",
                    "https://mastercardconnect.com/resources",
                    "https://mastercardconnect.com/announcements"
                ]
                
                for url in possible_urls:
                    try:
                        self.driver.get(url)
                        time.sleep(3)
                        # Verifica se carregou uma página válida
                        if "404" not in self.driver.page_source.lower():
                            logger.info(f"Acessou TRC via: {url}")
                            break
                    except:
                        continue
                        
            # Agora procura por Announcements
            announcements_selectors = [
                'a[href*="announcement"]',
                'a:contains("Announcement")',
                'a:contains("Anúncios")',
                '.announcement-link',
                '#announcements'
            ]
            
            announcements_link = None
            for selector in announcements_selectors:
                try:
                    if ':contains(' in selector:
                        text = selector.split(':contains(')[1].split(')')')[0].strip('\"')
                        xpath_selector = f"//a[contains(text(), '{text}') or contains(@title, '{text}')]"
                        announcements_link = self.driver.find_element(By.XPATH, xpath_selector)
                    else:
                        announcements_link = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"Link Announcements encontrado: {selector}")
                    break
                except:
                    continue
                    
            if announcements_link:
                logger.info("Clicando em Announcements...")
                self.driver.execute_script("arguments[0].click();", announcements_link)
                time.sleep(3)
                return True
            else:
                logger.warning("Link de Announcements não encontrado")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao navegar para announcements: {e}")
            return False
            
    def find_previous_week_documents(self):
        """Encontra documentos da semana anterior baseado na Publication Date"""
        logger.info("Procurando documentos da semana anterior...")
        
        week_start, week_end = self.get_previous_week_dates()
        
        # Formatos de data possíveis no site
        date_formats = [
            "%d %b %Y",  # 24 Jun 2025
            "%d %B %Y",  # 24 June 2025
            "%b %d, %Y", # Jun 24, 2025
            "%B %d, %Y", # June 24, 2025
            "%Y-%m-%d",  # 2025-06-24
            "%d/%m/%Y",  # 24/06/2025
            "%m/%d/%Y"   # 06/24/2025
        ]
        
        documents_to_download = []
        
        try:
            # Aguarda a página de announcements carregar
            time.sleep(3)
            
            # Procura por elementos que contenham datas
            date_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Publication Date') or contains(text(), 'Date') or contains(text(), '2025') or contains(text(), '2024')]")
            
            logger.info(f"Encontrados {len(date_elements)} elementos com possíveis datas")
            
            for element in date_elements:
                try:
                    text = element.text.strip()
                    
                    # Procura por datas no texto
                    for date_format in date_formats:
                        try:
                            # Extrai possíveis datas do texto
                            words = text.split()
                            for i, word in enumerate(words):
                                try:
                                    # Tenta diferentes combinações de palavras para formar uma data
                                    for length in [1, 2, 3, 4]:
                                        if i + length <= len(words):
                                            date_str = " ".join(words[i:i+length])
                                            doc_date = datetime.strptime(date_str, date_format)
                                            
                                            # Verifica se está na semana anterior
                                            if week_start <= doc_date <= week_end:
                                                logger.info(f"Documento da semana anterior encontrado: {date_str}")
                                                
                                                # Procura por botão/link de download próximo a este elemento
                                                download_link = self.find_download_link_near_element(element)
                                                if download_link:
                                                    documents_to_download.append({
                                                        'date': doc_date,
                                                        'date_str': date_str,
                                                        'download_link': download_link,
                                                        'text': text
                                                    })
                                                    
                                except ValueError:
                                    continue
                                    
                        except:
                            continue
                            
                except Exception as e:
                    logger.debug(f"Erro ao processar elemento: {e}")
                    continue
                    
            logger.info(f"Total de documentos da semana anterior encontrados: {len(documents_to_download)}")
            return documents_to_download
            
        except Exception as e:
            logger.error(f"Erro ao procurar documentos: {e}")
            return []
            
    def find_download_link_near_element(self, element):
        """Encontra link/botão de download próximo ao elemento de data"""
        try:
            # Procura no mesmo elemento pai
            parent = element.find_element(By.XPATH, "./..")
            
            # Seletores para botões/links de download
            download_selectors = [
                './/a[contains(@href, "download") or contains(@href, ".zip")]',
                './/button[contains(@class, "download")]',
                './/a[contains(@class, "download")]',
                './/i[contains(@class, "download")]/../..',  # Ícone de download
                './/span[contains(@class, "download")]/../..',
                './/a[contains(text(), "Download")]',
                './/button[contains(text(), "Download")]'
            ]
            
            for selector in download_selectors:
                try:
                    download_element = parent.find_element(By.XPATH, selector)
                    logger.info("Botão/link de download encontrado próximo ao elemento de data")
                    return download_element
                except:
                    continue
                    
            # Se não encontrou no parent direto, procura em siblings
            try:
                siblings = parent.find_elements(By.XPATH, "./following-sibling::*")
                for sibling in siblings[:3]:  # Verifica até 3 siblings
                    for selector in download_selectors:
                        try:
                            download_element = sibling.find_element(By.XPATH, "." + selector[2:])  # Remove ./
                            logger.info("Botão/link de download encontrado em sibling")
                            return download_element
                        except:
                            continue
            except:
                pass
                
            return None
            
        except Exception as e:
            logger.debug(f"Erro ao procurar download link: {e}")
            return None
            
    def download_documents(self, documents):
        """Faz download dos documentos encontrados"""
        logger.info(f"Iniciando download de {len(documents)} documentos...")
        
        downloaded_files = []
        
        for i, doc in enumerate(documents):
            try:
                logger.info(f"Baixando documento {i+1}/{len(documents)}: {doc['date_str']}")
                
                # Clica no link de download
                self.driver.execute_script("arguments[0].click();", doc['download_link'])
                
                # Aguarda o download começar
                time.sleep(3)
                
                # Verifica se arquivo foi baixado
                downloaded_file = self.wait_for_download()
                if downloaded_file:
                    downloaded_files.append({
                        'file': downloaded_file,
                        'date': doc['date'],
                        'date_str': doc['date_str']
                    })
                    logger.info(f"Download concluído: {downloaded_file}")
                else:
                    logger.warning(f"Download falhou para documento de {doc['date_str']}")
                    
            except Exception as e:
                logger.error(f"Erro ao baixar documento {doc['date_str']}: {e}")
                continue
                
        logger.info(f"Downloads concluídos: {len(downloaded_files)} arquivos")
        return downloaded_files
        
    def wait_for_download(self, timeout=30):
        """Aguarda um arquivo ser baixado"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Lista arquivos no diretório de download
            files = list(self.download_dir.glob("*"))
            
            # Procura por arquivos que não sejam .crdownload (downloads em progresso)
            complete_files = [f for f in files if not f.name.endswith('.crdownload')]
            
            if complete_files:
                # Retorna o arquivo mais recente
                newest_file = max(complete_files, key=lambda f: f.stat().st_mtime)
                return newest_file
                
            time.sleep(1)
            
        return None
        
    def extract_pdfs_from_zips(self, downloaded_files):
        """Extrai PDFs dos arquivos ZIP baixados"""
        logger.info("Extraindo PDFs dos arquivos ZIP...")
        
        extracted_pdfs = []
        
        for file_info in downloaded_files:
            file_path = file_info['file']
            
            try:
                if file_path.suffix.lower() == '.zip':
                    logger.info(f"Extraindo ZIP: {file_path.name}")
                    
                    # Cria diretório para este ZIP
                    extract_dir = self.pdf_dir / f"{file_info['date_str'].replace(' ', '_').replace('/', '_')}"
                    extract_dir.mkdir(exist_ok=True)
                    
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        for member in zip_ref.namelist():
                            if member.lower().endswith('.pdf'):
                                # Extrai apenas PDFs
                                zip_ref.extract(member, extract_dir)
                                extracted_pdf = extract_dir / member
                                extracted_pdfs.append({
                                    'pdf_path': extracted_pdf,
                                    'original_zip': file_path,
                                    'date': file_info['date'],
                                    'date_str': file_info['date_str']
                                })
                                logger.info(f"PDF extraído: {member}")
                                
                elif file_path.suffix.lower() == '.pdf':
                    # Já é um PDF, apenas move para o diretório correto
                    pdf_dest = self.pdf_dir / file_path.name
                    shutil.copy2(file_path, pdf_dest)
                    extracted_pdfs.append({
                        'pdf_path': pdf_dest,
                        'original_zip': None,
                        'date': file_info['date'],
                        'date_str': file_info['date_str']
                    })
                    logger.info(f"PDF copiado: {file_path.name}")
                    
            except Exception as e:
                logger.error(f"Erro ao extrair {file_path}: {e}")
                continue
                
        logger.info(f"Total de PDFs extraídos: {len(extracted_pdfs)}")
        return extracted_pdfs
        
    def run_weekly_collection(self):
        """Executa a coleta semanal completa"""
        logger.info("=== INICIANDO COLETA SEMANAL DE PDFs MASTERCARD ===")
        
        try:
            # Configura navegador
            self.setup_chrome()
            
            # Faz login
            if not self.login_to_mastercard():
                logger.error("Falha no login. Abortando coleta.")
                return False
                
            # Aguarda usuário confirmar login manualmente se necessário
            input("\nPressione ENTER após fazer login manualmente (se necessário)...")
                
            # Navega para announcements
            if not self.navigate_to_announcements():
                logger.error("Falha ao navegar para announcements. Abortando coleta.")
                return False
                
            # Procura documentos da semana anterior
            documents = self.find_previous_week_documents()
            if not documents:
                logger.warning("Nenhum documento da semana anterior encontrado.")
                return True
                
            # Faz download dos documentos
            downloaded_files = self.download_documents(documents)
            if not downloaded_files:
                logger.warning("Nenhum arquivo foi baixado.")
                return True
                
            # Extrai PDFs dos ZIPs
            extracted_pdfs = self.extract_pdfs_from_zips(downloaded_files)
            
            # Relatório final
            logger.info("=== COLETA CONCLUÍDA ===")
            logger.info(f"Documentos encontrados: {len(documents)}")
            logger.info(f"Arquivos baixados: {len(downloaded_files)}")
            logger.info(f"PDFs extraídos: {len(extracted_pdfs)}")
            
            for pdf in extracted_pdfs:
                logger.info(f"  - {pdf['pdf_path'].name} (Data: {pdf['date_str']})")
                
            return True
            
        except Exception as e:
            logger.error(f"Erro durante coleta: {e}")
            return False
            
        finally:
            if self.driver:
                logger.info("Fechando navegador...")
                self.driver.quit()
                
    def cleanup_downloads(self):
        """Limpa arquivos de download temporários"""
        try:
            for file in self.download_dir.glob("*"):
                if file.suffix.lower() == '.zip':
                    file.unlink()
                    logger.info(f"Arquivo ZIP removido: {file.name}")
        except Exception as e:
            logger.error(f"Erro ao limpar downloads: {e}")

def main():
    """Função principal"""
    collector = MastercardWeeklyCollector()
    
    try:
        success = collector.run_weekly_collection()
        
        if success:
            logger.info("Coleta executada com sucesso!")
            
            # Opcional: limpa ZIPs após extrair PDFs
            collector.cleanup_downloads()
            
        else:
            logger.error("Coleta falhou.")
            
    except KeyboardInterrupt:
        logger.info("Coleta interrompida pelo usuário.")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main() 