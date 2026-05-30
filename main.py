import telebot
from telebot import types

# Твой токен от BotFather
TOKEN = "8764622835:AAHeIwKotrfs5cBwxKdn1XhuYFsL3OfiHr8"
bot = telebot.TeleBot(TOKEN)

# Генерируем 250 пин-кодов (от ZE1000 до ZE1249)
# Они хранятся в оперативной памяти бота
AVAILABLE_PINS = [f"ZE{i}" for i in range(1000, 1250)]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Создаем клавиатуру с одной кнопкой
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
    # Ответ на нажатие кнопки
    bot.send_message(message.chat.id, "📎 Пожалуйста, прикрепите файл вашей квитанции в формате PDF и отправьте его сюда.")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    # Проверяем, является ли прикрепленный файл именно PDF
    if message.document.mime_type == 'application/pdf':
        
        # Проверяем, остались ли еще свободные ПИН-коды
        if len(AVAILABLE_PINS) > 0:
            # Берем первый доступный пин-код и удаляем его из списка выданных
            pin = AVAILABLE_PINS.pop(0)
            
            success_text = (
                "Квитанция успешно получена! ✅\n\n"
                "Ваш персональный пин-код для доступа к тесту:\n"
                f"`{pin}`\n\n"
                "Вернитесь на сайт платформы, нажмите «Ввести пин-код» и активируйте доступ."
            )
            # parse_mode='Markdown' делает текст пин-кода моноширинным, чтобы его было удобно копировать по клику
            bot.send_message(message.chat.id, success_text, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "К сожалению, свободные пин-коды закончились. Пожалуйста, обратитесь в поддержку.")
            
    else:
        # Если отправили картинку (jpg/png) или другой формат файла
        bot.send_message(message.chat.id, "⚠️ Это не похоже на PDF-файл. Пожалуйста, сохраните квитанцию из Kaspi именно в формате PDF и отправьте её снова.")

# Запуск бота в режиме постоянного опроса (Long Polling)
if __name__ == '__main__':
    bot.infinity_polling()