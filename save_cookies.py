from playwright.sync_api import sync_playwright
import json
import logging

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("save_cookies.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def save_cookies():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Direkte Navigation zur E-Mail-Login-Seite
        page.goto("https://www.tiktok.com/login/phone-or-email/email")
        logger.info("Navigiere zur E-Mail-Login-Seite.")
        logger.info("Logge dich manuell in TikTok ein...")
        
        # Wartezeit von 1 Minute, um den Login abzuschließen
        page.wait_for_timeout(60000)

        # Cookies nach dem Login speichern
        cookies = context.cookies()
        with open("tiktok_cookies.json", "w") as f:
            json.dump(cookies, f)
        logger.info("Cookies gespeichert in 'tiktok_cookies.json'.")
        browser.close()

if __name__ == "__main__":
    save_cookies()
