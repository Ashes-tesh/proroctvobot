import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

PHRASES_FILE = "phrases.txt"

def load_phrases():
    """Завантажує фрази з файлу, створює файл з дефолтними фразами якщо не існує"""
    if not os.path.exists(PHRASES_FILE):
        default_phrases = [
            "Нікому в чаті не подобається з тобою спілкуватися"
        ]
        with open(PHRASES_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(default_phrases))
    
    with open(PHRASES_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник команди /start"""
    await update.message.reply_text("🔮 Привіт! Я бот-пророк. Просто тегни мене у чаті, щоб отримати пророцтво")

async def add_phrase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Додає нову фразу у файл"""
    new_phrase = " ".join(context.args).strip()
    
    if not new_phrase:
        await update.message.reply_text("ℹ️ Використання: /addphrase [текст пророцтва]")
        return
    
    with open(PHRASES_FILE, "a", encoding="utf-8") as f:
        f.write("\n" + new_phrase)
    
    await update.message.reply_text(f"✅ Додано нове пророцтво: «{new_phrase}»")

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє згадку бота навіть неповну"""
    message = update.message
    if not message or not message.text:
        return

    bot_username = (await context.bot.get_me()).username.lower()
    text_lower = message.text.lower()

    # Перевірка повного та часткового тега
    if f"@{bot_username}" in text_lower or text_lower.startswith(f"@{bot_username[:3]}"):
        phrases = load_phrases()
        if not phrases:
            await message.reply_text("⚠️ Фрази відсутні! Адмін повинен додати їх у phrases.txt")
            return
        
        chosen_phrase = random.choice(phrases)
        user = message.from_user
        username = f"@{user.username}" if user.username else user.first_name
        response = f"Пророцтво для {username}:\n\n«{chosen_phrase}»"
        await message.reply_text(response)

if __name__ == "__main__":
    if not os.path.exists(PHRASES_FILE):
        load_phrases()

    TOKEN = os.getenv("BOT_TOKEN") or "8247991767:AAEanpHubh2T-WZziZywInqJwo5XS6oBGUc"

    app = ApplicationBuilder().token(TOKEN).build()

    # Команди
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addphrase", add_phrase))

    # Обробник згадок та тексту
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mention))

    print("🔮 Бот-пророк запущено! Напиши /start щоб почати")
    app.run_polling()