import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scraper import check_prices
from db import get_all_tracked, update_price
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_prices, 'interval', minutes=5)  # Check prices every 5 minutes
    scheduler.start()
    
    # Keep the script running
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")


if __name__ == "__main__":
    asyncio.run(main())

