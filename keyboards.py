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

one_but = types.KeyboardButton('1')
two_but = types.KeyboardButton('2')
three_but = types.KeyboardButton('3')
not_but = types.KeyboardButton('Не показывать')
hotels_num = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(one_but, two_but, three_but)
photos_num = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    one_but,
    two_but,
    three_but,
    not_but
)

calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_in = CallbackData('Дата заселения', 'action', 'year', 'month', 'day')
calendar_out = CallbackData('Дата отъезда', 'action', 'year', 'month', 'day')
