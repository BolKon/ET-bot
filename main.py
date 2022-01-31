import os
import telebot

import loaders
import rapid
import handlers
from telebot import types
from telebot.types import InputMediaPhoto
from dotenv import load_dotenv

load_dotenv('.env')
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.from_user.id, 'Вас приветствует Easy Travel бот - бот для поиска отелей в Вашем городе.\n'
                                           'Для уточнения списка команд введите /help')


@bot.message_handler(commands=['help'])
def com_help(message):
    bot.reply_to(message, 'Доступные команды:\n /lowprice - поиск самых дешёвых отелей в городе\n '
                          '/highprice - поиск самых дорогих отелей в городе\n '
                          '/bestdeal - поиск отелей наиболее подходящих по цене и удалённости от центра города\n '
                          '/history - вывод истории поиска отелей')


@bot.message_handler(commands=['lowprice'])
def lowprice(message):
    com_id = 'lp'
    bot.send_message(message.from_user.id, 'Введите название города:')
    bot.register_next_step_handler(message, city, com_id)


def city(message, com_id):
    se_ci = handlers.search_city
    se_ci['query'] = message.text
    search_res = rapid.search_city(se_ci)
    city_list = rapid.get_city_list(search_res, message.text)
    if not city_list:
        bot.send_message(message.from_user.id, 'К сожалению по данному названию ничего не найдено.\n'
                                               '  Попробуйте начать сначала.')
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i_but in city_list:
            but = types.KeyboardButton(i_but)
            markup.add(but)
        bot.send_message(message.from_user.id, text='Выберите один вариант из предложенных:', reply_markup=markup)
        bot.register_next_step_handler(message, city_hotels, search_res, com_id)


def city_hotels(message, search_res, com_id):
    if com_id == 'lp':
        qu = handlers.lp
    elif com_id == 'hp':
        qu = handlers.hp
    else:
        qu = handlers.bd
    city_ident = rapid.get_city_id(search_res, message.text)
    qu['destinationId'] = city_ident
    bot.send_message(
        message.from_user.id,
        text='Выберите денежную единицу для подсчета стоимости',
        reply_markup=loaders.mark_currency
                     )
    bot.register_next_step_handler(message, hotels_number, qu)


def hotels_number(message, qu):
    qu['currency'] = message.text
    bot.send_message(message.from_user.id, text='Сколько отелей показать?', reply_markup=loaders.hotels_num)
    bot.register_next_step_handler(message, num_photos, qu)


def num_photos(message, qu):
    hotels_n = int(message.text)
    ph_flag = True
    bot.send_message(message.from_user.id, text='Сколько фотографий отелей показать?', reply_markup=loaders.photos_num)
    bot.register_next_step_handler(message, show_hotels, qu, hotels_n, ph_flag)


def show_hotels(message, qu, hotels_n, ph_flag):
    hotels_dct = rapid.get_hotels_dict(qu)
    hotels_list = rapid.get_hotels(hotels_n, hotels_dct)
    if message.text == 'Не показывать':
        for i_hotel in hotels_list:
            bot.send_message(message.from_user.id, 'Название:\n    {name}\n'
                                                   'Адрес:\n    {address}\n'
                                                   'Расстояние до центра:\n    {c_center}\n'
                                                   'Цена за сутки:\n    {current}'.format(name=i_hotel['name'],
                                                                                          address=i_hotel['address'],
                                                                                          c_center=i_hotel['c_center'],
                                                                                          current=i_hotel['current']
                                                                                          )
                             )
    else:
        photos_n = int(message.text)
        for i_hotel in hotels_list:
            qs = {'id': i_hotel['id']}
            p_dct = rapid.get_photos(qs)
            hot_text = 'Название:\n    {name}\n' \
                       'Адрес:\n    {address}\n' \
                       'Расстояние до центра:\n    {c_center}\n'\
                       'Цена за сутки:\n   {current}'.format(name=i_hotel['name'],
                                                             address=i_hotel['address'],
                                                             c_center=i_hotel['c_center'],
                                                             current=i_hotel['current'])
            p_lst = rapid.get_photos_lst(p_dct, photos_n, hot_text)
            bot.send_media_group(message.from_user.id, p_lst)


@bot.message_handler(commands=['highprice'])
def highrice(message):
    com_id = 'hp'
    bot.send_message(message.from_user.id, 'Введите название города:')
    bot.register_next_step_handler(message, city, com_id)


@bot.message_handler(commands=['bestdeal'])
def bestdeal(message):
    com_id = 'bd'
    bot.send_message(message.from_user.id, 'Введите название города:')
    bot.register_next_step_handler(message, city, com_id)


@bot.message_handler(commands=['history'])
def history(message):
    pass


bot.infinity_polling()
