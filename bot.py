import os
import random
import logging
import telebot
from telebot.types import Message, MessageEntity
from flask import Flask

# Створюємо Flask додаток
app = Flask(__name__)

@app.route('/')
def home():
    return "🔮 Telegram Prediction Bot is running!", 200

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

PHRASES_FILE = "phrases.txt"
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

def load_phrases():
    """Завантажує фрази з файлу, створює файл з дефолтними фразами якщо не існує"""
    if not os.path.exists(PHRASES_FILE):
        default_phrases = [
        ]
        with open(PHRASES_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(default_phrases))
    
    with open(PHRASES_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

@bot.message_handler(commands=['start'])
def start(message: Message):
    """Обробник команди /start"""
    bot.reply_to(message, "🔮 Привіт! Я бот-пророк. Просто тегни мене у чаті, щоб отримати предсказание")

@bot.message_handler(commands=['addphrase'])
def add_phrase(message: Message):
    """Додає нову фразу у файл"""
    if not message.text or len(message.text.split()) < 2:
        bot.reply_to(message, "ℹ️ Використання: /addphrase [текст пророцтва]")
        return
        
    new_phrase = " ".join(message.text.split()[1:]).strip()
    
    with open(PHRASES_FILE, "a", encoding="utf-8") as f:
        f.write("\n" + new_phrase)
    
    bot.reply_to(message, f"✅ Додано нове пророцтво: «{new_phrase}»")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message: Message):
    """Обробляє всі повідомлення, шукаючи згадки бота"""
    try:
        if not message.text:
            return
            
        bot_username = bot.get_me().username.lower()
        
        # Перевіряємо згадки у повідомленні
        if message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    mentioned_text = message.text[entity.offset:entity.offset + entity.length].lower()
                    
                    if mentioned_text == f"@{bot_username}":
                        phrases = load_phrases()
                        if not phrases:
                            bot.reply_to(message, "⚠️ Фрази відсутні! Адмін повинен додати їх у phrases.txt")
                            return
                        
                        chosen_phrase = random.choice(phrases)
                        username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
                        response = f"Пророцтво для {username}:\n\n«{chosen_phrase}»"
                        bot.reply_to(message, response)
                        return
    except Exception as e:
        logger.error(f"Помилка обробки повідомлення: {e}")

def run_flask():
    """Запускає Flask сервер"""
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Створюємо файл з фразами при першому запуску
    if not os.path.exists(PHRASES_FILE):
        load_phrases()
    
    # Запускаємо Flask у окремому потоці
    import threading
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    logger.info("🔮 Бот-пророк запущено! Напиши /start щоб почати")
    logger.info("🌐 Flask сервер запущено на порті %s", os.environ.get('PORT', 8080))
    bot.infinity_polling()

