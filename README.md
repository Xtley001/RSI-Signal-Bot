# RSI Monitoring Bot

The RSI Monitoring Bot is an automated trading application that monitors the Relative Strength Index (RSI) for all derivative trading pairs on Bybit. The bot sends Telegram alerts to notify the user when the RSI approaches the overbought or oversold levels. With this information, traders can make more informed decisions.

Please note that this is not financial advice.
## Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Xtley001/RSI-Signal-Bot.git
    ```

2. **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up environment variables:**
    ```bash
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token
    TELEGRAM_CHAT_ID=your_telegram_chat_id
    BYBIT_API_KEY=your bybit api-key
    BYBIT_API_SECRET=your bybit api secret
    ```

4. **Run the bot:**
    ```bash
    python rsi_bot.py
    ```

## Commands

- `/start`: Start the bot.
- `/stop`: Stop the bot.


"# RSI-Signal-Bot" 
