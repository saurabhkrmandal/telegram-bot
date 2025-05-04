TARGET_USER_ID = None
from flask import Flask
import threading
import asyncio
import nest_asyncio  # Important fix for Replit's event loop
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# Flask web server to keep bot alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    thread = threading.Thread(target=run)
    thread.start()

# Telegram bot credentials
import os
BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_USER_ID = 1681983920




# Handler for payment screenshots
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or "No username"

    # Forward photo to admin
    await context.bot.forward_message(
        chat_id=ADMIN_USER_ID,
        from_chat_id=update.effective_chat.id,
        message_id=update.message.message_id
    )

    # Also notify who sent it
    await context.bot.send_message(
        chat_id=ADMIN_USER_ID,
        text=f"📷 Photo received from {username} (ID: {user_id})"
    )

    await update.message.reply_text("Screenshot received! We'll verify and give you access soon.")

# Handler for text messages
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or "No username"
    message = update.message.text

    # Forward to you (admin)
    await context.bot.send_message(
        chat_id=ADMIN_USER_ID,
        text=f"📩 New message from {username} (ID: {user_id}):\n{message}"
    )

    await update.message.reply_text("Message received! We'll get back to you soon.")

# Allow admin to reply manually
async def manual_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("You're not authorized to use this command.")
        return

    try:
        user_id = int(context.args[0])
        message_type = context.args[1].lower()
        content = ' '.join(context.args[2:])

        if message_type == "text":
            await context.bot.send_message(chat_id=user_id, text=content)

        elif message_type == "photo":
            await context.bot.send_photo(chat_id=user_id, photo=content)

        elif message_type == "video":
            await context.bot.send_video(chat_id=user_id, video=content)

        elif message_type == "document":
            await context.bot.send_document(chat_id=user_id, document=content)

        else:
            await update.message.reply_text("❌ Unsupported message type. Use text/photo/video/document.")
            return

        await update.message.reply_text("✅ Message sent.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

        # Forward media
        async def forward_admin_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TARGET_USER_ID

    if update.effective_user.id != ADMIN_USER_ID:
        return

    if not TARGET_USER_ID:
        await update.message.reply_text("❌ You haven't set a target user.\nUse /target <user_id> first.")
        return

    try:
        # Forward photo/video/document to the target user
        await context.bot.copy_message(
            chat_id=TARGET_USER_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )

        await update.message.reply_text(f"✅ Media forwarded to user ID {TARGET_USER_ID}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# Respond to /start
# Respond to /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or "No username"
    first_name = user.first_name or "No name"

    # Send welcome message to user
    await update.message.reply_text(
        "🎉 *Congratulations!* You're among the *first 5 users!* 💎\n"
        "Enjoy my *premium membership* at just *₹299 or $3/month* 💖\n\n"
        "*Paypal:* [paypal.me/ala288500](https://www.paypal.me/ala288500)\n"
        "*UPI:* `bratyoung42@okicici`\n\n"
        "👉 _Send your payment screenshot here and get access now_ 🔥",
        parse_mode="Markdown"
    )

    # Notify admin
    await context.bot.send_message(
        chat_id=ADMIN_USER_ID,
        text=(
            "📥 *New user started the bot!*\n"
            f"👤 *Name:* {first_name}\n"
            f"🔗 *Username:* @{username}\n"
            f"🆔 *User ID:* `{user_id}`"
        ),
        parse_mode="Markdown"
    )



# Start everything
if __name__ == '__main__':
    keep_alive()
    nest_asyncio.apply()  # Apply fix for nested event loop (Replit)

    async def set_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TARGET_USER_ID

    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("Not authorized.")
        return

    try:
        TARGET_USER_ID = int(context.args[0])
        await update.message.reply_text(f"✅ Target user set to ID: {TARGET_USER_ID}")
    except:
        await update.message.reply_text("❌ Invalid usage. Use: /target <user_id>")

    async def main():
        app_bot = ApplicationBuilder().token(BOT_TOKEN).build()

        app_bot.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        app_bot.add_handler(CommandHandler("start", start_command))
        app_bot.add_handler(CommandHandler("reply", manual_reply))
        app_bot.add_handler(CommandHandler("target", set_target))
        app_bot.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, forward_admin_media))




        print("Bot is running...")
        await app_bot.run_polling()

    asyncio.get_event_loop().run_until_complete(main())
