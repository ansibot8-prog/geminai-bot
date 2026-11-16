import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_KEY")

MODEL = "gemini-2.0-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_API_KEY}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola, soy GeminAI ✨ ¿Qué quieres que hagamos?")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pregunta = update.message.text
    await update.message.reply_text("Pensando... 🤔")

    try:
        data = {
            "contents": [{"parts": [{"text": pregunta}]}]
        }
        r = requests.post(URL, json=data, timeout=30)
        resultado = r.json()

        if "candidates" in resultado:
            texto = resultado["candidates"][0]["content"]["parts"][0]["text"]
            await update.message.reply_text(texto)
        else:
            await update.message.reply_text("Google no contestó, intenta de nuevo en un ratito.")
            print(resultado)

    except Exception as e:
        await update.message.reply_text("Se atoró Google, intenta de nuevo en un ratito.")
        print(f"Error: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    print("Bot corriendo...")
    app.run_polling()
