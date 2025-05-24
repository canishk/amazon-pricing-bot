import requests
import asyncio
import logging
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from telegram import Bot
from db import get_all_tracked, update_price
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def get_amazon_price(asin: str) -> float | None:
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "en-IN,en;q=0.9",
    }
    url = f"https://www.amazon.in/dp/{asin}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "lxml")

        price_tag = soup.select_one("span.a-price-whole")
        if price_tag:
            logging.info(f"[Scraper] Found price tag: {price_tag}")
            price_text = price_tag.text.replace(",", "").strip()
            logging.info(f"[Scraper] Extracted price text: {price_text}")
            if price_text.startswith("₹"):
                price_text = price_text[1:].strip()
            return float(price_text)
    except Exception as e:
        logging.exception(f"[Scraper Error] {e}")
    return None

async def check_prices():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    tracked_products = await get_all_tracked()
    logging.info(f"Checking prices for {len(tracked_products)} tracked products.")
    if not tracked_products:
        logging.info("No tracked products found.")
        return
    logging.info(f"Tracked products: {tracked_products}")
    for user_id, asin, last_known_price in tracked_products:
        message = ""
        logging.info(f"User {user_id} - ASIN {asin} - Last known price: {last_known_price}")
        if user_id is None:
            continue
        new_price = await get_amazon_price(asin)
        logging.info(new_price)
        if new_price is None:
            logging.error(f"Failed to fetch price for ASIN {asin}.")
            return
        if new_price < last_known_price or last_known_price is None:
            await update_price(asin, new_price)
            if last_known_price is None:
                message = f"The product https://www.amazon.in/dp/{asin} is now available at ₹{new_price}."
            else:
                message = f"The price of the product https://www.amazon.in/dp/{asin} has reduced to ₹{new_price}."
        elif new_price > last_known_price:
            message = f"The price of the product https://www.amazon.in/dp/{asin} has increased to ₹{new_price}."
        logging.info(f"User {user_id} - ASIN {asin} - Last known price: {last_known_price}, New price: {new_price}")
        if message !="":
            logging.info(f"Sending message to user {user_id}: {message}")
            await bot.send_message(chat_id=user_id, text=message)

if __name__ == "__main__":
    asyncio.run(check_prices())