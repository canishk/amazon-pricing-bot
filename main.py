import asyncio
from bot.telegram_bot import TelegramBot
from scheduler.price_checker import PriceChecker
from config import Config
from db.database import Database

async def main():
    config = Config()
    token = config.get(key="TELEGRAM_BOT_TOKEN")
    db_file = config.get("DB_FILE", "tracked_products.db")
    db = Database(db_file)
    await db.init_db()

    bot = TelegramBot(token, db_file)
    checker  = PriceChecker(db,bot)
    
    checker.start()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())  # This works in VSCode terminal now