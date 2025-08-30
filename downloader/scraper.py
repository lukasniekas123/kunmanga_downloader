import cloudscraper
from bs4 import BeautifulSoup
import re
import json

BASE_URL = "https://kunmanga.com"

class KunMangaScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(browser="chrome")
        self.scraper.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
            "Referer": BASE_URL,
        })
        cookies = self.load_cookies()
        if cookies and 'cf_clearance' in cookies:
            self.scraper.cookies.set("cf_clearance", cookies['cf_clearance'], domain="kunmanga.com")
        else:
            print("Warning: 'cf_clearance' cookie not found. Scraping may fail.")

    def load_cookies(self):
        """Loads cookies from a JSON file."""
        try:
            with open('cookies.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def get_manga_metadata(self, manga_url: str):
        print(f"🌐 Fetching: {manga_url}")
        try:
            resp = self.scraper.get(manga_url)
            resp.raise_for_status()
        except Exception as e:
            print(f"❌ Failed to fetch page: {e}")
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        title_elem = soup.select_one("div.post-title h1")
        title = title_elem.text.strip() if title_elem else "Unknown Title"

        chapters = []
        for link in soup.select("ul.main.version-chap li.wp-manga-chapter a"):
            chapter_title = link.text.strip()
            chapter_url_data = link.get("href")
            if isinstance(chapter_url_data, list):
                chapter_url = chapter_url_data[0] if chapter_url_data else ''
            else:
                chapter_url = chapter_url_data

            if chapter_url and not chapter_url.startswith("http"):
                chapter_url = f"{BASE_URL}{chapter_url}"
            
            chapter_number_match = re.search(r'Chapter\s*(\d+(\.\d+)?)', chapter_title, re.IGNORECASE)
            if chapter_number_match:
                chapter_number = float(chapter_number_match.group(1))
                chapters.append({
                    'number': chapter_number,
                    'url': chapter_url
                })

        chapters.sort(key=lambda c: c['number'])
        
        return {
            'title': title,
            'chapters': chapters
        }

    def get_chapter_images(self, chapter_url: str):
        try:
            resp = self.scraper.get(chapter_url)
            resp.raise_for_status()
        except Exception as e:
            print(f"❌ Failed to fetch chapter page: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        image_urls = []
        for image_element in soup.select('div.reading-content img.wp-manga-chapter-img'):
            src_data = image_element.get('src')
            if isinstance(src_data, str):
                image_urls.append(src_data.strip())
            elif isinstance(src_data, list) and src_data:
                image_urls.append(src_data[0].strip())
        return image_urls

# Functions to be called from other modules
def get_manga_metadata(manga_url):
    scraper = KunMangaScraper()
    return scraper.get_manga_metadata(manga_url)

def get_chapter_images(chapter_url):
    scraper = KunMangaScraper()
    return scraper.get_chapter_images(chapter_url)
