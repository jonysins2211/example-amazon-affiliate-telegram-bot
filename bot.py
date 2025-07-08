from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from constants import *
from create_messages import create_product_post
from amazon_api import AmazonAPI

bot = Bot(token=TELEGRAM_TOKEN)

# Optional: Only allow specific user(s)
AUTHORIZED_USERS = [949657126]  # Replace with your Telegram user ID

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'Benvenuto 💀 {update.effective_user.first_name}, send me an Amazon product link '
        'to create the post in your channel!'
    )

# message handler for Amazon product links
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Safety check: message must exist and be text
    if not update.message or not update.message.text:
        return

    # Optional: restrict access to authorized users only
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return

    message_text = update.message.text.strip()

    # Check if it's an Amazon product link
    if 'amazon.' in message_text and '/dp/' in message_text:
        amazon_api = AmazonAPI()

        try:
            # Get product details from the Amazon API
            product = amazon_api.get_product_from_url(message_text)

            if not product:
                await update.message.reply_text("⚠️ Could not fetch product details. Please check the link.")
                return

            # Format the message
            formatted_message = create_product_post(product)

            # Send to channel
            await bot.send_message(chat_id=CHANNEL_ID, text=formatted_message, parse_mode='HTML')

            # Confirm to user
            await update.message.reply_text("✅ Product posted to the channel!")

        except Exception as e:
            await update.message.reply_text(f"❌ An error occurred: {e}")
    else:
        await update.message.reply_text("⚠️ Please send a valid Amazon product link.")

# Setup and run the bot
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler('start', start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

app.run_polling()
