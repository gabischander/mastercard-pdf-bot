#!/usr/bin/env python3
"""
Mastercard PDF Bot - Versão Corrigida
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

class MastercardBotFixed:
    def __init__(self):
        self.download_dir = Path("mastercard_pdfs")
        self.download_dir.mkdir(exist_ok=True)
        
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("prefs", {
            "download.default_directory": str(self.download_dir.absolute()),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True
        })
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 15)
    
    def debug_page(self):
        """Debug da página atual"""
        logger.info(f"URL: {self.driver.current_url}")
        logger.info(f"Título: {self.driver.title}")
        screenshot = f"debug_{int(time.time())}.png"
        self.driver.save_screenshot(screenshot)
        logger.info(f"Screenshot: {screenshot}")

def main():
    logger.info("🚀 Testando bot corrigido...")
    bot = MastercardBotFixed()
    
    try:
        # Teste básico
        bot.driver.get("https://trc-techresource.mastercard.com")
        time.sleep(3)
        bot.debug_page()
        
    finally:
        bot.driver.quit()

if __name__ == "__main__":
    main()
