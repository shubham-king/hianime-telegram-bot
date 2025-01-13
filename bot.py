import logging
import os
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from telegram.constants import ParseMode

# Configuration
my_bot_token = '7610200608:AAFdG-h0mvgNdjkrJq0fRXoYHiiXoKSq-yI'
CHANNEL_USERNAME = "@toonwav"  # Channel to force subscription
CHANNEL_URL = "https://t.me/toonwav"  # Channel URL for force subscription
ADMIN_ID = 5771629925
USERS_FILE = "users.json"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)
logger = logging.getLogger(__name__)

# User management
def save_users(users):
    """Save the list of users to the JSON file."""
    with open(USERS_FILE, "w") as file:
        json.dump(users, file)


def load_users():
    """Load the list of users from the JSON file."""
    if not os.path.exists(USERS_FILE):
        save_users([])  # Create the file with an empty list if missing
    try:
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        save_users([])  # Reset if file is invalid
        return []


async def force_subscription(update: Update) -> bool:
    """Check if the user is subscribed to the channel."""
    try:
        user_status = await update.get_bot().get_chat_member(CHANNEL_USERNAME, update.effective_user.id)
        return user_status.status in ["member", "administrator", "creator"]
    except Exception:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    user = update.effective_user
    users = load_users()
    if user.id not in users:
        users.append(user.id)
        save_users(users)  # Save user after adding

    is_subscribed = await force_subscription(update)
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("Subscribe to Channel", url=CHANNEL_URL)],
            [InlineKeyboardButton("Check Subscription", callback_data="check_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Welcome, {user.first_name}! to Hianime Powered Bot.\n\n➥ You must subscribe to our channel to use this bot.",
            reply_markup=reply_markup,
        )
        return

    # Admin-specific buttons
    if user.id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("Support", url="https://t.me/Internet_Verse")],
            [InlineKeyboardButton("Admin Panel", callback_data="admin_panel")],
            [InlineKeyboardButton("Hianime.to", web_app=WebAppInfo(url="https://1xanimes.org"))],
            [InlineKeyboardButton("Toonwav", web_app=WebAppInfo(url="https://xplayvine.blogspot.com/"))],
        ]
    else:
        # User buttons
        keyboard = [
            [InlineKeyboardButton("Support", url="https://t.me/Internet_Verse")],
            [InlineKeyboardButton("Japanese/English", web_app=WebAppInfo(url="https://1xanimes.org"))],
            [InlineKeyboardButton("Hindi/Tamil/Telugu", web_app=WebAppInfo(url="https://xplayvine.blogspot.com/"))],  # New WebApp Button
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 Hi {user.first_name}! , I am Anime Powered Bot to Stream Anime.\nUse me to Watch your favorit anime in SUB or DUB and also in Local Language like Hindi, Tamil, Telugu & more.\n\n➥ Language Available: Japanese | English | Hindi | Tamil | Telugu\n\n*Note: you cant play new released animes, takes some time to load* \n\nMade with ❤️ for YOU! ",
        reply_markup=reply_markup,
    )


async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback to check subscription status."""
    query = update.callback_query
    is_subscribed = await force_subscription(update)
    if is_subscribed:
        await query.answer("✅ Subscription verified!  You can now use the bot.\n\n© Toonwav", show_alert=True)
        await query.edit_message_text("Good Job! You are now Subscribed. Use /start to begin.")
    else:
        await query.answer("❌ You are not subscribed. Please subscribe to continue.\n\n© Toonwav", show_alert=True)


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin panel for broadcasting and stats."""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("You are not authorized to access the admin panel.")
        return

    keyboard = [
        [InlineKeyboardButton("Broadcast Message", callback_data="broadcast")],
        [InlineKeyboardButton("View Stats", callback_data="view_stats")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "Admin Panel:\nChoose an option.",
        reply_markup=reply_markup,
    )


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Broadcast a message to all users."""
    query = update.callback_query
    await query.edit_message_text("Send the message you want to broadcast:")
    context.user_data["broadcast"] = True


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle messages for broadcasting."""
    if context.user_data.get("broadcast"):
        users = load_users()  # Ensure users are loaded
        message = update.message.text
        for user_id in users:
            try:
                await context.bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)
            except Exception as e:
                logger.warning(f"Failed to send message to {user_id}: {e}")
        await update.message.reply_text("Message broadcasted to all users.")
        context.user_data["broadcast"] = False


async def view_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View bot statistics."""
    users = load_users()
    await update.callback_query.edit_message_text(f"Total users: {len(users)}")


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(my_bot_token).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    application.add_handler(CallbackQueryHandler(check_subscription, pattern="^check_subscription$"))
    application.add_handler(CallbackQueryHandler(broadcast, pattern="^broadcast$"))
    application.add_handler(CallbackQueryHandler(view_stats, pattern="^view_stats$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Get the port from environment variable or use default
    port = int(os.environ.get("PORT", 5000))  # Render assigns a dynamic port

    # Run the bot
    application.run_polling(port=port)  # Bind to the correct port


if __name__ == "__main__":
    main()
