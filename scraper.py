from playwright.sync_api import sync_playwright
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def scrape_trending_videos(limit=50):
    logger.info("Starte das Scraping von Trending-Videos...")
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1"
            )
            page = context.new_page()
            page.goto("https://www.tiktok.com/trending?lang=en")
            logger.info("TikTok-Trending-Seite geladen.")

            # Cookie-Popup schließen
            try:
                logger.info("Warte auf Cookie-Popup...")
                accept_button = page.wait_for_selector("button:has-text('Allow all')", timeout=10000)
                if accept_button:
                    accept_button.click()
                    logger.info("Cookies akzeptiert.")
            except Exception as e:
                logger.warning(f"Cookie-Popup wurde nicht gefunden: {e}")

            # Schließe das "Get the full experience"-Popup
            try:
                logger.info("Warte auf das 'Get the full experience'-Popup...")
                not_now_button = page.wait_for_selector("button:has-text('Not Now')", timeout=10000)
                if not_now_button:
                    not_now_button.click()
                    logger.info("'Not Now' geklickt, Popup geschlossen.")
            except Exception as e:
                logger.warning(f"'Get the full experience'-Popup wurde nicht gefunden: {e}")

            # Warten auf Video-Elemente
            page.wait_for_selector("div[data-e2e='video-item']", timeout=15000)
            videos = page.query_selector_all("div[data-e2e='video-item']")
            logger.info(f"Gefundene Video-Elemente: {len(videos)}")

            videos_data = []
            for idx, video in enumerate(videos[:limit]):
                try:
                    author = video.query_selector("a[data-e2e='user-info-username']").inner_text()
                    views = video.query_selector("strong[data-e2e='video-views']").inner_text()
                    description = video.query_selector("p[data-e2e='video-desc']").inner_text()
                    hashtags = [tag.inner_text() for tag in video.query_selector_all("a[data-e2e='challenge-tag']")]

                    videos_data.append({
                        "author": author,
                        "views": views,
                        "description": description,
                        "hashtags": hashtags,
                    })
                    logger.info(f"Video {idx+1}: Autor={author}, Views={views}, Hashtags={hashtags}")
                except Exception as e:
                    logger.error(f"Fehler beim Extrahieren von Video {idx+1}: {e}")

            # Speichern der Daten
            df = pd.DataFrame(videos_data)
            csv_path = "data/trending_videos_playwright.csv"
            df.to_csv(csv_path, index=False)
            logger.info(f"Erfolgreich {len(videos_data)} Videos gesammelt und in '{csv_path}' gespeichert.")

        except Exception as e:
            logger.error(f"Fehler beim Scraping: {e}")

        finally:
            browser.close()
            logger.info("Browser geschlossen.")

if __name__ == "__main__":
    scrape_trending_videos(limit=50)
