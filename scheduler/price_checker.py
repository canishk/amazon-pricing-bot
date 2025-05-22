import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from db.database import Database
from config import Config
from scraper.amazon import AmazonScraper



class PriceChecker:
    def __init__(self, db: Database, bot: Bot):
        self.db = db
        self.bot = bot
        self.scheduler = AsyncIOScheduler()

    async def check_prices(self):
        tracked_products = await self.db.get_all_tracked()
        for telegram_id, asin, last_known_price in tracked_products:
            new_price = AmazonScraper().get_price(asin)
            if new_price is not None and new_price < last_known_price:
                await self.db.update_price(telegram_id, asin, new_price)
                await self.bot.send_message(
                    chat_id=telegram_id, 
                    text=f"Price dropped for ASIN {asin}: ₹{new_price}"
                )

    def start(self):
        self.scheduler.add_job(self.check_prices, 'interval', minutes=120)
        self.scheduler.start()
        print("Price checker started.")
if __name__ == "__main__":  
    config = Config()
    db_file = config.get("DB_FILE", "tracked_products.db")
    token = config.get("TELEGRAM_BOT_TOKEN")
    db = Database(db_file)
    bot = Bot(token)
    price_checker = PriceChecker(db, bot)
    asyncio.run(db.init_db())
    price_checker.start()
    asyncio.get_event_loop().run_forever()
