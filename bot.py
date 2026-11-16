import requests, os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

GEMINI_KEY = os.getenv("GEMINI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola, soy GeminAI ✨ ¿Qué quieres que hagamos?")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pregunta = update.message.text
    await update.message.reply_text("Pensando... 🤔")
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_KEY}"
        data = {"contents": [{"parts": [{"text": pregunta}]}]}
        r = requests.post(url, json=data, timeout=60)
        j = r.json()
        print(j)
        if "candidates" not in j:
            await update.message.reply_text(f"Error Gemini: {j}")
            return
        respuesta = j["candidates"][0]["content"]["parts"][0]["text"]
        await update.message.reply_text(respuesta)
    except Exception as e:
        await update.message.reply_text(f"Se atoró: {e}")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
print("Bot corriendo...")
app.run_polling()