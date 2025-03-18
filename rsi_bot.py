import os
import asyncio
import logging
import ccxt
import pandas as pd
import pandas_ta as ta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Bybit Exchange with API keys
exchange = ccxt.bybit({
    'apiKey': os.getenv("BYBIT_API_KEY"),  # Add your Bybit API key
    'secret': os.getenv("BYBIT_API_SECRET"),  # Add your Bybit API secret
    'rateLimit': 500,  # Add a delay between requests (in milliseconds)
    'enableRateLimit': True,  # Enable rate limiting
})

# Telegram Bot Token and Chat ID from .env
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Constants
RSI_OVERBOUGHT = 70  # RSI threshold for overbought (shorting opportunities)
RSI_OVERSOLD = 30  # RSI threshold for oversold (buying opportunities)
TIME_FRAME = '5m'  # 5-minute timeframe
MONITOR_INTERVAL = 1  # Check every 1 second (adjust as needed)

# List of strong derivative pairs to exclude from shorting
STRONG_PAIRS = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'BNB/USDT:USDT', 'SOL/USDT:USDT', 'XRP/USDT:USDT']

# Global variables
monitoring_active = False  # Controls whether the monitoring loop is active

# Fetch All Derivative Pairs from Bybit
def get_derivative_pairs():
    """
    Fetches all derivative trading pairs on Bybit.
    """
    try:
        # Fetch markets from Bybit
        markets = exchange.fetch_markets()
        logger.info(f"Markets fetched: {len(markets)} pairs")  # Debugging
        
        # Filter for derivative pairs (linear and inverse perpetual contracts)
        derivative_pairs = [market['symbol'] for market in markets if market['linear'] or market['inverse']]
        logger.info(f"Derivative pairs found: {len(derivative_pairs)}")
        
        return derivative_pairs  # Return all derivative pairs
    except Exception as e:
        logger.error(f"Error fetching markets: {e}")
        return []

# Calculate RSI Using pandas_ta
async def get_rsi(symbol, timeframe=TIME_FRAME, period=14):
    """
    Fetches OHLCV data for a symbol and calculates the RSI using pandas_ta.
    """
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
        if not ohlcv or len(ohlcv) < period:  # Skip if insufficient data
            logger.warning(f"Insufficient data for {symbol}")
            return symbol, None
        
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['rsi'] = ta.rsi(df['close'], length=period)
        return symbol, df['rsi'].iloc[-1]  # Return the symbol and latest RSI value
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return symbol, None

# Function to Send Telegram Notifications
async def send_telegram_message(application, message):
    """
    Sends a message to the specified Telegram chat.
    """
    try:
        await application.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode="Markdown"  # Enable Markdown formatting
        )
        logger.info(f"Telegram message sent: {message}")
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")

# Function to Monitor RSI Levels for Autonomous Alerts
async def monitor_rsi(application):
    """
    Monitors the RSI for all derivative pairs and sends alerts for extreme RSI levels.
    """
    global monitoring_active
    
    while monitoring_active:
        try:
            # Fetch all derivative pairs
            derivative_pairs = get_derivative_pairs()
            
            # Process each pair one at a time
            for pair in derivative_pairs:
                if not monitoring_active:
                    break  # Stop if monitoring is deactivated
                
                # Fetch RSI for the pair
                symbol, rsi = await get_rsi(pair)
                if rsi is None:
                    continue  # Skip if RSI couldn't be calculated
                
                # Check for extreme RSI levels
                if rsi >= RSI_OVERBOUGHT and pair not in STRONG_PAIRS:  # Overbought condition (exclude strong pairs)
                    alert_message = f"🚨 **Overbought Signal (Short):**\n{pair}: RSI {rsi:.2f}"
                    await send_telegram_message(application, alert_message)
                elif rsi <= RSI_OVERSOLD and pair in STRONG_PAIRS:  # Oversold condition (only for strong pairs)
                    alert_message = f"🚨 **Oversold Signal (Buy):**\n{pair}: RSI {rsi:.2f}"
                    await send_telegram_message(application, alert_message)
                
                # Add a small delay to avoid hitting rate limits
                await asyncio.sleep(MONITOR_INTERVAL)
        
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
        
        # Add a small delay before restarting the loop
        await asyncio.sleep(MONITOR_INTERVAL)

# Telegram Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /start command.
    """
    global monitoring_active
    
    if monitoring_active:
        await update.message.reply_text("✅ Bot is already running.")
        return
    
    monitoring_active = True
    await update.message.reply_text("🚀 Starting RSI monitoring...")
    
    # Start the monitoring loop as a background task
    asyncio.create_task(monitor_rsi(application))

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /stop command.
    """
    global monitoring_active
    
    if not monitoring_active:
        await update.message.reply_text("✅ Bot is already stopped.")
        return
    
    monitoring_active = False
    await update.message.reply_text("🛑 Stopping RSI monitoring...")

# Main Function to Run the Bot
async def main():
    """
    Initializes and runs the Telegram bot.
    """
    global application
    # Initialize the Telegram Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))

    # Start the Bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # Keep the application running
    while True:
        await asyncio.sleep(1)

# Run the Bot
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")