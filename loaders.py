from telebot import types

rub_button = types.KeyboardButton('RUB')
usd_button = types.KeyboardButton('USD')
mark_currency = types.ReplyKeyboardMarkup(resize_keyboard=True).add(rub_button, usd_button)

one_but = types.KeyboardButton('1')
two_but = types.KeyboardButton('2')
three_but = types.KeyboardButton('3')
not_but = types.KeyboardButton('Не показывать')
hotels_num = types.ReplyKeyboardMarkup(resize_keyboard=True).add(one_but, two_but, three_but)
photos_num = types.ReplyKeyboardMarkup(resize_keyboard=True).add(one_but, two_but, three_but, not_but)