import os
import random
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(name)  # Виправлено: name замість name

PHRASES_FILE = "phrases.txt"

def load_phrases():
    """Завантажує фрази з файлу, створює файл з дефолтними фразами якщо не існує"""
    if not os.path.exists(PHRASES_FILE):
        default_phrases = [
        ]
        with open(PHRASES_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(default_phrases))
    
    with open(PHRASES_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник команди /start"""
    await update.message.reply_text("🔮 Привіт! Я бот-пророк. Просто тегни мене у чаті, щоб отримати предсказание")

async def add_phrase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Додає нову фразу у файл"""
    if not context.args:
        await update.message.reply_text("ℹ️ Використання: /addphrase [текст пророцтва]")
        return
        
    new_phrase = " ".join(context.args).strip()
    
    with open(PHRASES_FILE, "a", encoding="utf-8") as f:
        f.write("\n" + new_phrase)
    
    await update.message.reply_text(f"✅ Додано нове пророцтво: «{new_phrase}»")

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє звернення до бота через тег у чаті"""
    try:
        message = update.message
        if not message or not message.text:
            return
            
        user = message.from_user
        bot = await context.bot.get_me()
        bot_username = bot.username.lower()
        
        # Перевіряємо згадки у повідомленні
        for entity in message.entities:
            if entity.type == "mention":
                mentioned_text = message.text[entity.offset:entity.offset + entity.length].lower()
                
                if mentioned_text == f"@{bot_username}":
                    phrases = load_phrases()
                    if not phrases:
                        await message.reply_text("⚠️ Фрази відсутні! Адмін повинен додати їх у phrases.txt")
                        return
                    
                    chosen_phrase = random.choice(phrases)
                    username = f"@{user.username}" if user.username else user.first_name
                    response = f"Пророцтво для {username}:\n\n«{chosen_phrase}»"
                    await message.reply_text(response)
                    return
                    
    except Exception as e:
        logger.error(f"Помилка обробки згадки: {e}")

def main() -> None:
    """Запуск бота"""
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        logger.error("Токен бота не знайдено! Встановіть змінну середовища BOT_TOKEN")
        return
    
    try:
        # Створюємо Application
        application = Application.builder().token(TOKEN).build()
        
        # Реєстрація обробників команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("addphrase", add_phrase))
        
        # Обробник тегів у повідомленнях
        application.add_handler(MessageHandler(
            filters.TEXT & filters.Entity("mention"),
handle_mention
        ))
        
        # Запуск бота
        logger.info("🔮 Бот-пророк запущено! Напиши /start щоб почати")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Помилка запуску бота: {e}")

if name == "main":
    # Створюємо файл з фразами при першому запуску
    if not os.path.exists(PHRASES_FILE):
        load_phrases()
    main()
