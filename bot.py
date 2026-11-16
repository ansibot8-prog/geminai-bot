import os
import threading
import requests
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_KEY")

URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-20b"

app_web = Flask(__name__)
@app_web.route("/")
def home():
    return "GeminAI con Groq vivo!"

def correr_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola, soy GeminAI ✨ ¿Qué quieres que hagamos?")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pregunta = update.message.text
    await update.message.reply_text("Pensando... 🤔")
    try:
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "Eres GeminAI. Si el usuario pide algo largo (cuento, historia, explicación, resumen, tutorial) lo das COMPLETO y largo. Nunca lo dejes a medias."},
                {"role": "user", "content": pregunta}
            ],
            "temperature": 0.8,
            "max_tokens": 2000
        }
        r = requests.post(URL, headers=headers, json=payload, timeout=40)
        j = r.json()
        if "choices" in j:
            texto = j["choices"][0]["message"]["content"]
            # Telegram solo deja 4096 caracteres, lo partimos
            for i in range(0, len(texto), 4000):
                await update.message.reply_text(texto[i:i+4000])
        else:
            await update.message.reply_text(f"Error de Groq: {str(j)[:400]}")
    except Exception as e:
        await update.message.reply_text(f"Se atoró: {e}")

if __name__ == "__main__":
    threading.Thread(target=correr_web, daemon=True).start()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    print("Bot corriendo con Groq...")
    app.run_polling()
