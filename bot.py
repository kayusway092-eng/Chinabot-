import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Bot Content ---

TOPICS_TEXT = {
    "blockchain": (
        "What is Blockchain?\n\n"
        "A blockchain is a decentralized, digital ledger (like a notebook) that records transactions "
        "across many computers. Once a record (a 'block') is added to the chain, it's "
        "very difficult to change, making it secure and transparent.\n\n"
        "Think of it as a shared Google Doc that everyone can see but no one can alter "
        "after the fact."
    ),
    "wallets": (
        "How to Secure Your Crypto (Wallets)\n\n"
        "A crypto wallet stores your 'private keys'—the secret passwords that give you "
        "access to your coins. \n\n"
        "1. Hot Wallets (Software): These are apps on your phone or computer (e.g., MetaMask, Trust Wallet). "
        "They are convenient but connected to the internet, making them less secure.\n\n"
        "2. Cold Wallets (Hardware): These are physical devices (e.g., Ledger, Trezor) that "
        "store your keys offline. They are the most secure way to store your crypto.\n\n"
        "Rule #1: NEVER share your private key or 'seed phrase' with anyone. If you lose it, you lose your crypto."
    ),
    "market_cap": (
        "What is Market Cap?\n\n"
        "Market Capitalization (or 'Market Cap') is the total value of a cryptocurrency. "
        "It's a simple calculation:\n\n"
        "Market Cap = (Current Price of 1 Coin) x (Total Number of Coins in Circulation)\n\n"
        "It's used to understand the relative size of a crypto. A coin with a $1 price and 100 billion "
        "coins ($100B Market Cap) is much 'bigger' than a coin with a $1,000 price and 1 million "
        "coins ($1B Market Cap)."
    )
}

SUPPORT_TEXT = (
    "If you need help or have a question, please contact our admin: t.me/Logan207\n\n"
    "Note: Admin will NEVER ask you for money, private keys, or passwords."
)

# --- Bot Handlers ---

# Define states for conversation
MAIN_MENU, TOPIC_MENU = range(2)

def get_main_menu_keyboard():
    """Returns the main menu keyboard."""
    keyboard = [
        [KeyboardButton("Topics")],
        [KeyboardButton("Helpful Channels"), KeyboardButton("Contact Support")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_topics_menu_keyboard():
    """Returns the topics menu keyboard."""
    keyboard = [
        [KeyboardButton("What is Blockchain?")],
        [KeyboardButton("How to Secure Your Crypto")],
        [KeyboardButton("What is Market Cap?")],
        [KeyboardButton("Back to Main Menu")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends a welcome message and displays the main menu."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! 👋\n\n"
        "Welcome to the Crypto Trading Educator bot. "
        "My purpose is to provide simple, safe, and clear information about "
        "cryptocurrency and trading concepts.\n\n"
        "Please choose an option from the menu below to get started.",
        reply_markup=get_main_menu_keyboard(),
    )
    return MAIN_MENU

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles main menu button presses."""
    text = update.message.text
    if text == "Topics":
        await update.message.reply_text(
            "Here are our current educational topics. Select one to learn more:",
            reply_markup=get_topics_menu_keyboard()
        )
        return TOPIC_MENU
    
    # --- THIS BLOCK IS UPDATED ---
    elif text == "Helpful Channels":
        # The direct image link is now added
        photo_url = "https://i.postimg.cc/mD8c5yB4/image.png"
        
        try:
            # Try to send the photo with the caption
            await update.message.reply_photo(
                photo=photo_url,
                caption="Coming soon"
            )
        except Exception as e:
            # If the link is bad or broken, send a text message instead
            logger.error(f"Error sending photo. Link: {photo_url}, Error: {e}")
            await update.message.reply_text("Coming soon")
            
        return MAIN_MENU
    # --- END OF UPDATE ---

    elif text == "Contact Support":
        await update.message.reply_text(SUPPORT_TEXT)
        return MAIN_MENU
    else:
        await update.message.reply_text(
            "Sorry, I didn't understand that. Please use the buttons.",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU

async def topic_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles topic menu button presses."""
    text = update.message.text
    if text == "What is Blockchain?":
        await update.message.reply_text(TOPICS_TEXT["blockchain"])
        return TOPIC_MENU
    elif text == "How to Secure Your Crypto":
        await update.message.reply_text(TOPICS_TEXT["wallets"])
        return TOPIC_MENU
    elif text == "What is Market Cap?":
        await update.message.reply_text(TOPICS_TEXT["market_cap"])
        return TOPIC_MENU
    elif text == "Back to Main Menu":
        await update.message.reply_text(
            "Returning to the main menu.",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU
    else:
        await update.message.reply_text(
            "Sorry, I didn't understand that. Please use the topic buttons or go back.",
            reply_markup=get_topics_menu_keyboard()
        )
        return TOPIC_MENU

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles any message that is not part of a conversation."""
    await update.message.reply_text(
        "Sorry, I'm not sure what to do with that. "
        "Try pressing /start to see the main menu.",
        reply_markup=get_main_menu_keyboard()
    )

def main() -> None:
    """Run the bot."""
    # Get the token from environment variables
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN environment variable not set!")
        return

    # Create the Application
    application = Application.builder().token(token).build()

    # Add conversation handler with states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                MessageHandler(
                    filters.Regex("^(Topics|Helpful Channels|Contact Support)$"), main_menu_handler
                )
            ],
            TOPIC_MENU: [
                MessageHandler(
                    filters.Regex("^(What is Blockchain\?|How to Secure Your Crypto|What is Market Cap\?|Back to Main Menu)$"),
                    topic_menu_handler
                )
            ],
        },
        fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, fallback)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    logger.info("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()


