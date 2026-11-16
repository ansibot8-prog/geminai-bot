import os
import threading
import requests
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_KEY")

MODEL = "gemini-2.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_API_KEY}"

app_web = Flask(__name__)
@app_web.route("/")
def home():
    return "Bot vivo!"

def correr_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola, soy GeminAI ✨ ¿Qué quieres que hagamos?")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pregunta = update.message.text
    await update.message.reply_text("Pensando... 🤔")
    try:
        data = {"contents": [{"parts": [{"text": pregunta}]}]}
        r = requests.post(URL, json=data, timeout=30)
        resultado = r.json()
        if "candidates" in resultado:
            texto = resultado["candidates"][0]["content"]["parts"][0]["text"]
            await update.message.reply_text(texto)
        else:
            await update.message.reply_text(f"Error de Google: {r.status_code} - {str(resultado)[:400]}")
            print(resultado)
    except Exception as e:
        await update.message.reply_text(f"Se atoró: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    threading.Thread(target=correr_web, daemon=True).start()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    print("Bot corriendo...")
    app.run_polling()
