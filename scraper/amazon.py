import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class AmazonScraper:
    def __init__(self):
        self.ua = UserAgent()

    def get_price(self, asin: str) -> float | None:
        headers = {
            "User-Agent": self.ua.random,
            "Accept-Language": "en-IN,en;q=0.9"
        }
        url = f"https://www.amazon.in/dp/{asin}"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "lxml")
            price_tag = soup.select_one("#priceblock_dealprice, #priceblock_ourprice, .a-price .a-offscreen")
            if price_tag:
                return float(price_tag.text.replace("₹", "").replace(",", "").strip())
        except Exception as e:
            print(f"[Scraper Error] {e}")
        return None

