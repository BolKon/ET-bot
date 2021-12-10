import telebot
import nltk

bot = telebot.TeleBot('BOT_TOKEN')


def clean(text: str) -> str:
    """Функция удаляет небуквенные символы из текста и возвращает только буквенный текст"""

    clean_text = ''
    for char in text.lower():
        if char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
            clean_text += char
    return clean_text


@bot.message_handler(commands=['start', 'hello_world'])
def send_welcome(message):
    bot.send_message(message.from_user.id, "Привет! Как твои дела?")


@bot.message_handler()
def hello(message):
    text = clean(message.text.lower())
    if text == 'привет':
        bot.send_message(message.from_user.id, "Привет! Как твои дела?")
    elif nltk.edit_distance('привет', text) / max(6, len(text)) < 0.4:
        bot.send_message(message.from_user.id, "Привет! Как твои дела?")


bot.infinity_polling()
