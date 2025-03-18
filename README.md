# RSI Monitoring Bot

This bot monitors the Relative Strength Index (RSI) for the top 100 trading pairs on Bybit. It sends Telegram alerts when the RSI approaches overbought or oversold levels. 
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
    export TELEGRAM_BOT_TOKEN=your_telegram_bot_token
    export TELEGRAM_CHAT_ID=your_telegram_chat_id
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
