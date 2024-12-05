from playwright.sync_api import sync_playwright
import json
import logging

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scrape_with_cookies.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def scrape_with_cookies():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.90 Safari/537.36",
        viewport={"width": 1280, "height": 720}
        )

        # Cookies aus der Datei laden und ungültige `sameSite`-Werte korrigieren
        with open("tiktok_cookies.json", "r") as f:
            cookies = json.load(f)

        # Korrigiere die `sameSite`-Werte
        for cookie in cookies:
            if cookie.get("sameSite") not in ["Strict", "Lax", "None"]:
                logger.warning(f"Korrigiere `sameSite`-Wert für Cookie: {cookie['name']}")
                cookie["sameSite"] = "None"  # Standardwert setzen

        context.add_cookies(cookies)
        logger.info("Cookies erfolgreich geladen und hinzugefügt.")

        # TikTok-Seite aufrufen
        page = context.new_page()
        page.goto("https://www.tiktok.com/trending")
        logger.info("TikTok-Trending-Seite geöffnet.")
        page.wait_for_timeout(10000)  # Warten, um Inhalte zu laden

        # Überprüfen, ob die Seite korrekt geladen wurde
        if "Login" not in page.content():
            logger.info("Login erfolgreich. Inhalte wurden geladen.")
        else:
            logger.warning("Login fehlgeschlagen. Bitte überprüfe die Cookies.")
        
        browser.close()

if __name__ == "__main__":
    scrape_with_cookies()
