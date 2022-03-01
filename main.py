import json
import handlers
import keyboards
import loaders
import datetime
import random
from loguru import logger
from loaders import bot, Users, now, User, db
from telebot.types import CallbackQuery, ReplyKeyboardRemove, InputMediaPhoto
from keyboards import calendar, calendar_in, calendar_out


logger.add('info.log', format='{time} {message}', level='INFO', retention='10 days')


@bot.message_handler(commands=['start'])
def send_welcome(message) -> None:
    """
    Стартовая команда для бота. Отправляет приветственное сообщение со ссылкой на команду /help

    :param message:
    :type message: Message

    :return: None
    """
    bot.send_message(message.from_user.id, 'Вас приветствует Easy Travel бот - бот для поиска отелей в Вашем городе.\n'
                                           'Для уточнения списка команд введите /help')


@bot.message_handler(commands=['help'])
def com_help(message) -> None:
    """
    Команда отправляет пользователю сообщение со списком доступных команд и их описанием

    :param message:
    :type message: Message

    :return: None
    """
    bot.send_message(message.from_user.id, loaders.help_text)


@bot.message_handler(commands=['lowprice'])
def lowprice(message) -> None:
    """
    Команда запускает процесс поиска самых дешёвых отелей в городе

    :param message:
    :type message: Message

    :return: None
    """
    user = Users.get_user(message.from_user.id)
    user.date = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    user.command = '/lowprice'
    bot.send_message(message.from_user.id, 'Введите название города:')
    logger.info('main.lowprice\nGet user: {user}'.format(user=message.from_user.id))
    bot.register_next_step_handler(message, handlers.city, user)


@bot.message_handler(commands=['highprice'])
def highrice(message) -> None:
    """
    Команда запускает процесс поиска самых дорогих отелей в городе

    :param message:
    :type message: Message

    :return: None
    """
    user = Users.get_user(message.from_user.id)
    user.date = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    user.command = '/highprice'
    bot.send_message(message.from_user.id, 'Введите название города:')
    logger.info('main.highprice\nGet user: {user}'.format(user=message.from_user.id))
    bot.register_next_step_handler(message, handlers.city, user)


@bot.message_handler(commands=['bestdeal'])
def bestdeal(message) -> None:
    """
    Команда запускает процесс поиска отелей наиболее подходящих по цене и удалённости от центра города

    :param message:
    :type message: Message

    :return: None
    """
    user = Users.get_user(message.from_user.id)
    user.date = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    user.command = '/bestdeal'
    bot.send_message(message.from_user.id, 'Введите название города:')
    logger.info('main.bestdeal\nGet user: {user}'.format(user=message.from_user.id,))
    bot.register_next_step_handler(message, handlers.city, user)


@bot.message_handler(commands=['history'])
def history(message) -> None:
    """
    Команда отправляет пользователю историю его запросов к данному боту

    :param message:
    :type message: Message

    :return: None
    """
    user_id = message.from_user.id
    logger.info('main.history\nGet user: {user}'.format(user=message.from_user.id))
    with db:
        history_result = User.select().where(User.u_id == user_id)
        if not history_result:
            bot.send_message(message.from_user.id, 'История не найдена.')
        else:
            for user in history_result[-5:]:
                if user.command == '/bestdeal':
                    bot.send_message(message.from_user.id, 'Команда: {command}\n   Дата запроса: {date}\n'
                                                           'Параметры поиска:\n   Город: {city}'
                                                           '\n   Диапазон цен: {min_p}-{max_p} {cur}'
                                                           '\n   Расстояние от центра: {min_d}-{max_d} км'
                                                           '\n   Дата заселения: {ch_in}\n   Дата выселения: {ch_out}'.
                                     format(command=user.command, date=user.date, city=user.city, min_p=user.min_price,
                                            cur=user.currency, max_p=user.max_price, min_d=user.min_distance,
                                            max_d=user.max_distance, ch_in=user.check_in, ch_out=user.check_out))
                else:
                    bot.send_message(message.from_user.id, 'Команда: {command}\n   Дата запроса: {date}\n'
                                                           'Параметры поиска:\n   Город: {city}'
                                                           '\n   Дата заселения: {ch_in}\n   Дата выселения: {ch_out}'.
                                     format(command=user.command, date=user.date, city=user.city,
                                            ch_in=user.check_in, ch_out=user.check_out))
                if user.photos_check:
                    hot_list = json.loads(user.hotels)
                    photos_list = json.loads(user.photos_list)
                    for i_h_ind, i_hotel in enumerate(hot_list):
                        media_group = list()
                        for i_p_ind, i_photos in enumerate(photos_list):
                            if i_p_ind == i_h_ind:
                                for i_ph_ind, i_photo in enumerate(i_photos):
                                    if i_ph_ind == 0:
                                        media_group.append(InputMediaPhoto(i_photo, caption=i_hotel))
                                    else:
                                        media_group.append(InputMediaPhoto(i_photo))

                        bot.send_media_group(message.from_user.id, media_group)
                    bot.send_message(message.from_user.id, '==================')
                else:
                    hot_list = json.loads(user.hotels)
                    for i_hotel in hot_list:
                        bot.send_message(message.from_user.id, i_hotel)
                    bot.send_message(message.from_user.id, '==================')
    logger.info('Command completed.\n=================================================\n')
    bot.send_message(message.from_user.id, loaders.help_text)


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_in.prefix))
def callback_inline_in(call: CallbackQuery):
    """
    Обработка inline callback запросов calendar_in-календаря
    Функция запрашивает дату выезда из отеля

    :param call:
    :return:
    """
    user = Users.get_user(call.from_user.id)
    name, action, year, month, day = call.data.split(calendar_in.sep)
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    if action == "DAY":
        if date.strftime('%Y-%m-%d') < now.strftime('%Y-%m-%d'):
            bot.send_message(call.from_user.id,
                             text='Дата заселения не может быть меньше сегодняшней.',
                             reply_markup=calendar.create_calendar(
                                 name=calendar_in.prefix,
                                 year=now.year,
                                 month=now.month))
        else:
            user.check_in = date.strftime('%Y-%m-%d')
            bot.send_message(call.from_user.id, text=f'Дата заселения: {user.check_in}.\nВыберите дату выселения:',
                             reply_markup=calendar.create_calendar(
                                 name=calendar_out.prefix,
                                 year=now.year,
                                 month=now.month))
    elif action == 'CANCEL':
        logger.info('main.callback_inline_in -'
                    ' User canceled process.\n=================================================\n')
        bot.send_message(call.from_user.id,
                         'Операция отменена.\n\n{help}'.format(help=loaders.help_text),
                         reply_markup=ReplyKeyboardRemove())


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_out.prefix))
def callback_inline_out(call: CallbackQuery):
    """
    Обработка inline callback запросов calendar_out-календаря
    Функция запрашивает у пользователя количество отелей, которое нужно показать

    :param call:
    :return:
    """
    user = Users.get_user(call.from_user.id)
    name, action, year, month, day = call.data.split(calendar_out.sep)
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    if action == "DAY":
        if date.strftime('%Y-%m-%d') <= user.check_in:
            bot.send_message(call.from_user.id,
                             text=f'Дата выселения не может быть меньше даты заселения.'
                                  f'\nДата заселения: {user.check_in}',
                             reply_markup=calendar.create_calendar(
                                 name=calendar_out.prefix,
                                 year=now.year,
                                 month=now.month))
        else:
            user.check_out = date.strftime('%Y-%m-%d')
            bot.send_message(call.from_user.id, f'Дата заселения: {user.check_in}.\nДата выселения: {user.check_out}'
                                                f'\nСколько отелей показать?',
                             reply_markup=keyboards.hotels_num)
            bot.register_next_step_handler(call.message, handlers.num_photos, user)
    elif action == 'CANCEL':
        logger.info('main.callback_inline_out -'
                    ' User canceled process.\n=================================================\n')
        bot.send_message(call.from_user.id,
                         'Операция отменена.\n\n{help}'.format(help=loaders.help_text),
                         reply_markup=ReplyKeyboardRemove())


@bot.message_handler(content_types=['text'])
def random_message_text(message):
    bot.send_message(message.from_user.id, random.choice(loaders.rand_answer))
    bot.send_message(message.from_user.id, loaders.help_text)


bot.infinity_polling()
