import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running 24/7!"

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app_flask.run(host='0.0.0.0', port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🔥 البوت يعمل 24 ساعة بنجاح!')

def main():
    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    if not TOKEN:
        print("خطأ: TELEGRAM_TOKEN غير موجود")
        return

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    bot_thread = threading.Thread(target=lambda: application.run_polling())
    bot_thread.start()
    run_flask()

if __name__ == '__main__':
    main()