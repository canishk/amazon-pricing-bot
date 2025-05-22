from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from db.database import Database
from config import Config

class TelegramBot:
    def __init__(self, token, db_file):
        self.application = Application.builder().token(token).build()
        self.db = Database(db_file)
        # self.setup_handlers()

    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("track", self.track_product))
        # self.application.add_handler(CommandHandler("stop", self.stop_tracking))
        # self.application.add_handler(CommandHandler("list", self.list_tracked_products))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Welcome! Use /track <ASIN> to track a product.")

    async def track_product(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.args:
            asin = context.args[0]
            telegram_id = update.message.from_user.id
            await self.db.add_product(telegram_id, asin)
            await update.message.reply_text(f"Tracking product with ASIN: {asin}")
        else:
            await update.message.reply_text("Please provide an ASIN.")

    async def stop_tracking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.args:
            asin = context.args[0]
            telegram_id = update.message.from_user.id
            await self.db.remove_product(telegram_id, asin)
            await update.message.reply_text(f"Stopped tracking product with ASIN: {asin}")
        else:
            await update.message.reply_text("Please provide an ASIN.")

    async def list_tracked_products(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_id = update.message.from_user.id
        tracked_products = await self.db.get_tracked_products(telegram_id)
        if tracked_products:
            response = "Tracked products:\n" + "\n".join([f"ASIN: {asin}" for asin in tracked_products])
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("No products are being tracked.")
    
    async def run(self):
        await self.db.init_db()
        self.setup_handlers()
        await self.application.run_polling()

if __name__ == "__main__":
    config = Config()
    token = config.get("TELEGRAM_BOT_TOKEN")
    db_file = config.get("DB_FILE", "tracked_products.db")
    bot = TelegramBot(token, db_file)
    import asyncio
    asyncio.run(bot.run())
# This code is a simple Telegram bot that allows users to track Amazon products by their ASIN (Amazon Standard Identification Number).

