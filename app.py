import telebot
from telebot import types
import os
import threading
from flask import Flask

# --- 1. Настройка бота ---
TOKEN = "8764622835:AAHeIwKotrfs5cBwxKdn1XhuYFsL3OfiHr8"
bot = telebot.TeleBot(TOKEN)

# Генерируем 250 пин-кодов (от ZE1000 до ZE1249)
AVAILABLE_PINS = [f"ZE{i}" for i in range(1000, 1250)]

# --- 2. Твои обработчики сообщений (без изменений) ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Отправить PDF квитанцию")
    markup.add(btn1)
    welcome_text = (
        "Привет! Это бот ZagranEasy. 👋\n\n"
        "Чтобы получить доступ к IELTS Mock-тесту, нажмите кнопку ниже "
        "и отправьте нам PDF-квитанцию об оплате из приложения Kaspi."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Отправить PDF квитанцию")
def ask_for_pdf(message):
    bot.send_message(message.chat.id, "📎 Пожалуйста, прикрепите файл вашей квитанции в формате PDF и отправьте его сюда.")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if message.document.mime_type == 'application/pdf':
        if len(AVAILABLE_PINS) > 0:
            pin = AVAILABLE_PINS.pop(0)
            success_text = (
                "Квитанция успешно получена! ✅\n\n"
                "Ваш персональный пин-код для доступа к тесту:\n"
                f"`{pin}`\n\n"
                "Вернитесь на сайт платформы, нажмите «Ввести пин-код» и активируйте доступ."
            )
            bot.send_message(message.chat.id, success_text, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "К сожалению, свободные пин-коды закончились. Пожалуйста, обратитесь в поддержку.")
    else:
        bot.send_message(message.chat.id, "⚠️ Это не похоже на PDF-файл. Пожалуйста, сохраните квитанцию из Kaspi именно в формате PDF и отправьте её снова.")

# --- 3. Важная часть: Веб-сервер для Render ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running!"

# Запускаем бота в отдельном потоке, чтобы не блокировать Flask
def run_bot():
    # Убираем старый вызов if __name__ == '__main__'
    bot.infinity_polling(skip_pending=True)

if __name__ == '__main__':
    # Запускаем поток с ботом
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Запускаем Flask сервер на порту, который требует Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)