import telebot
from telebot import types
import os
import threading
from flask import Flask, jsonify

# --- 1. Настройка бота ---
TOKEN = "8764622835:AAHeIwKotrfs5cBwxKdn1XhuYFsL3OfiHr8"
bot = telebot.TeleBot(TOKEN)

# Генерируем 250 пин-кодов (от ZE1000 до ZE1249)
AVAILABLE_PINS = [f"ZE{i}" for i in range(1000, 1250)]

# --- 2. Твои обработчики сообщений ---
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

# --- 3. Веб-сервер для Render и healthcheck ---
app = Flask(__name__)

@app.route('/')
def health_check():
    """Основной endpoint для проверки здоровья бота"""
    return jsonify({
        "status": "alive",
        "bot": "ZagranEasy Bot",
        "available_pins": len(AVAILABLE_PINS),
        "message": "Bot is running correctly!"
    }), 200

@app.route('/health')
def health_check_alt():
    """Альтернативный endpoint для cron-job.org"""
    return jsonify({"status": "ok", "timestamp": os.popen('date').read().strip()}), 200

@app.route('/ping')
def ping():
    """Простой ping для быстрой проверки"""
    return "pong", 200

# --- 4. Запуск бота и веб-сервера ---
def run_bot():
    """Запускает Telegram бота в режиме polling"""
    print("🤖 Telegram бот запущен и готов к работе...")
    try:
        # Убираем webhook, если он был установлен ранее
        bot.remove_webhook()
        # Запускаем polling с обработкой ошибок
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"❌ Ошибка в работе бота: {e}")
        # Пытаемся перезапустить через 5 секунд
        threading.Timer(5.0, run_bot).start()

def run_web_server():
    """Запускает Flask сервер для healthcheck"""
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Веб-сервер запущен на порту {port}")
    print(f"✅ Healthcheck доступен по адресу: https://localhost:{port}/health")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    print("🚀 Запуск ZagranEasy бота...")
    print(f"📊 Доступно пин-кодов: {len(AVAILABLE_PINS)}")
    
    # Запускаем веб-сервер в основном потоке
    # А бота - в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем веб-сервер (он заблокирует основной поток)
    run_web_server()
