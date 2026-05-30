import os
import telebot
from telebot import types
from flask import Flask
from threading import Thread

# Инициализация Flask для Render
app = Flask('')

@app.route('/')
def home():
    return "Бот ZagranEasy активен!"

@app.route('/healthz')
def health():
    return "OK", 200

def run():
    # Render передает номер порта через переменную окружения PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Запускаем веб-сервер в отдельном потоке
t = Thread(target=run)
t.start()

# --- Логика бота ---
TOKEN = "8764622835:AAHeIwKotrfs5cBwxKdn1XhuYFsL3OfiHr8"
bot = telebot.TeleBot(TOKEN)

AVAILABLE_PINS = [f"ZE{i}" for i in range(1000, 1250)]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Отправить PDF квитанцию")
    markup.add(btn1)
    bot.send_message(message.chat.id, "Привет! Это бот ZagranEasy. 👋", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Отправить PDF квитанцию")
def ask_for_pdf(message):
    bot.send_message(message.chat.id, "📎 Прикрепите файл PDF квитанции.")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if message.document.mime_type == 'application/pdf':
        if len(AVAILABLE_PINS) > 0:
            pin = AVAILABLE_PINS.pop(0)
            bot.send_message(message.chat.id, f"Ваш пин-код: `{pin}`", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Коды закончились.")
    else:
        bot.send_message(message.chat.id, "⚠️ Нужно отправить именно PDF.")

if __name__ == '__main__':
    bot.infinity_polling()
