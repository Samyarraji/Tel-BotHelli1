from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import requests

# Replace with your bot token from @BotFather
BOT_TOKEN = "8461788424:AAGXE4rL9wLo81sQFdObs4txbk2Q0zjfvO8"

# Store registered users in memory (you can replace with DB later)
registered_users = {}

# --- Commands ---

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hi, Welcome to our bot!\n\n"
                                    "Please register first using /register")

# /register command
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ask user to share contact
    contact_button = KeyboardButton("📱 Share Contact", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text("Please share your contact to register:", reply_markup=reply_markup)

# Handle contact sharing
async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    contact = update.message.contact

    # Save user info
    registered_users[user.id] = {
        "first_name": contact.first_name,
        "last_name": contact.last_name,
        "phone": contact.phone_number,
    }

    await update.message.reply_text(
        f"✅ Registered successfully!\n\n"
        f"Name: {contact.first_name} {contact.last_name or ''}\n"
        f"Phone: {contact.phone_number}\n\n"
        f"Now you can use /price <currency> (example: /price bitcoin)"
    )

# /price command
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    # Check if user is registered
    if user.id not in registered_users:
        await update.message.reply_text("⚠️ You must register first using /register")
        return

    if not context.args:
        await update.message.reply_text("❓ Please provide a currency name. Example:\n/price bitcoin")
        return

    currency = context.args[0].lower()
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={currency}&vs_currencies=usd"
        response = requests.get(url).json()

        if currency in response:
            price_usd = response[currency]["usd"]
            await update.message.reply_text(f"💰 {currency.capitalize()} price: ${price_usd:,}")
        else:
            await update.message.reply_text("⚠️ Currency not found. Try another one.")
    except Exception as e:
        await update.message.reply_text("⚠️ Error fetching price. Please try again later.")

# --- Main Bot ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(CommandHandler("price", price))

    # Run bot
    app.run_polling()

if __name__ == "__main__":
    main()
