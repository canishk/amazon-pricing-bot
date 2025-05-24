# amazon-pricing-bot
Telegram Bot for Amazon Pricing Alerts

## Features

- Automatically monitors Amazon product prices.
- Sends instant Telegram alerts when prices drop below your set threshold.
- Supports tracking multiple products at once.
- Easy-to-use command-based interface for managing your watchlist.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/amazon-pricing-bot.git
    cd amazon-pricing-bot
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Configure your credentials:**
   - Set up your Amazon Product Advertising API keys and Telegram Bot token in a `.env` file or as environment variables.

2. **Start the bot:**
    ```bash
    python bot.py
    ```

3. **Interact with the bot on Telegram:**
   - Use commands to add products, set price thresholds, and manage your watchlist.

## How It Works

- The bot periodically checks the prices of products in your watchlist using the Amazon Product Advertising API.
- When a product's price drops below your specified threshold, the bot sends you a Telegram message with the product details and a link.

## Contributing

1. Fork the repository.
2. Create your feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/YourFeature`
5. Open a pull request.

## License

This project is licensed under the MIT License.