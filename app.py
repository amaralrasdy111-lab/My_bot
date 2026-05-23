import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==== توكن البوت (ضع التوكن الصحيح هنا) ====
TOKEN = "8547040724:AAGG6SCU5KHAxvCdEBH14nE73hh-cD3JhK4"

# ==== خادم Flask (لإبقاء Render سعيداً) ====
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_bot():
    """تشغيل البوت في خيط منفصل"""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    print("✅ البوت بدأ العمل...")
    application.run_polling()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 البوت يعمل 24 ساعة! ✅")

# ==== تشغيل الخادم والبوت معاً ====
if __name__ == "__main__":
    # تشغيل البوت في خلفية
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # تشغيل خادم Flask (لإبقاء التطبيق نشطاً)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
