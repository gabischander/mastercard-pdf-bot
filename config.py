"""
Configurações do Mastercard PDF Bot
"""
import os
from pathlib import Path

# URLs base
BASE_URL = "https://trc-techresource.mastercard.com"
LOGIN_URL = f"{BASE_URL}/login"
DOCS_URL = f"{BASE_URL}/resource-center/documents"

# Configurações de download
DOWNLOAD_DIR = Path("mastercard_pdfs")
MAX_DOWNLOADS = int(os.getenv('DOWNLOAD_LIMIT', 5))  # Limite padrão para teste
DOWNLOAD_TIMEOUT = 30  # segundos

# Configurações do Chrome
CHROME_OPTIONS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--window-size=1920,1080"
]

# Configurações de logging
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_FILE = 'mastercard_bot.log'
