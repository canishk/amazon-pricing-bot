import logging
import db
from scraper import get_amazon_price
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from config import TELEGRAM_BOT_TOKEN


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await db.init_db()  # Initialize the database
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome! Use /track <ASIN> to track a product.")
    await db.add_user(update.effective_chat.id)  # Add the user to the database
# This is a simple Telegram bot that responds to the /start command.

async def track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logging.info(f"User {user_id} is trying to track a product.")
    if len(context.args) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /track <ASIN>")
        return
    logging.info(f"Tracking product with ASIN: {context.args}")
    asin = context.args[0].upper()  # ASINs are typically uppercase
    if not asin.isalnum() or len(asin) != 10:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid ASIN format. Please provide a valid ASIN.")
        return
    # Check if the product is already being tracked
    existing_products = await db.get_user_products(user_id)
    if asin in existing_products:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"You are already tracking the product with ASIN: {asin}")
        return
    # Fetch the price of the product using the ASIN
    price = await get_amazon_price(asin)
    if price is None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Could not fetch the price for ASIN: {asin}. Please check the ASIN and try again.")
        return
    logging.info(f"Fetched price for ASIN {asin}: ₹{price}")
    # Add the product to the database
    await db.add_product(telegram_id=user_id, asin=asin, last_known_price=price)  # Add the product to the database

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Product with ASIN {asin} is now being tracked at ₹{price}.")
    # Log the addition of the product
    logging.info(f"Product with ASIN {asin} added to the database for user {user_id}.")
    # Here you would add the logic to track the product using the ASIN
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tracking product with ASIN: {asin}")
# This bot uses the python-telegram-bot library to create a simple Telegram bot that can respond to commands.


def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    # Add command handler
    start_handler = CommandHandler('start', start)
    track_handler = CommandHandler('track', track)
    application.add_handler(track_handler)
    application.add_handler(start_handler)
    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()