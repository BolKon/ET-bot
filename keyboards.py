from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
from telebot import types


def custom_keyboard(obj_list):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i_but in obj_list:
        but = types.KeyboardButton(i_but)
        markup.add(but)
    return markup


rub_button = types.KeyboardButton('RUB')
usd_button = types.KeyboardButton('USD')
mark_currency = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(rub_button, usd_button)

but1 = types.KeyboardButton('1')
but2 = types.KeyboardButton('2')
but3 = types.KeyboardButton('3')
but4 = types.KeyboardButton('4')
but5 = types.KeyboardButton('5')
but6 = types.KeyboardButton('6')
but7 = types.KeyboardButton('7')
but8 = types.KeyboardButton('8')
but9 = types.KeyboardButton('9')
but10 = types.KeyboardButton('10')
not_but = types.KeyboardButton('Не показывать')
hotels_num = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(but1, but2, but3, but4, but5,
                                                                                         but6, but7, but8, but9, but10)
photos_num = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(but1, but2, but3, but4,
                                                                                         but5, not_but)

calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_in = CallbackData('Дата заселения', 'action', 'year', 'month', 'day')
calendar_out = CallbackData('Дата отъезда', 'action', 'year', 'month', 'day')
