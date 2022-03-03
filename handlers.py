import loaders
import re
import rapid
import json
import keyboards
from loguru import logger
from telebot.types import InputMediaPhoto, ReplyKeyboardRemove
from models import User, db
from loaders import bot, now, Users, city_control_pat, hotels_control_pat, photos_control_pat
from keyboards import calendar, calendar_in


@logger.catch
def city(message, user) -> None:
    """
    Функция получает результат поиска города через API сайта
    и формирует из полученных результатов клавиатуру для более точного определения города для поиска отеля.
    Может определить на каком языке (русский или английский) делался запрос для выдачи более корректного результата.
    :param message:
    :param user:
    :type message: Message
    :type user: Users

    :return: None
    """
    se_ci = loaders.search_city
    se_ci['locale'] = 'ru_RU' if re.match(r'[А-Яа-яЁё]+', message.text) else 'en_US'
    se_ci['query'] = message.text
    logger.info('handlers.city - Input city: {city}'.format(city=message.text))
    search_res = rapid.get_rapid_json(se_ci, loaders.get_city_url, city_control_pat)
    if search_res == {'result': 'timeout'}:
        logger.info('handlers.city - ReadTimeout. '
                    'Process stopped!\n=================================================\n')
        bot.send_message(message.from_user.id, loaders.timeout_error_text)
    elif search_res == {'result': 'error'}:
        logger.info('handlers.city - Error! Process stopped!\n=================================================\n')
        bot.send_message(message.from_user.id, loaders.smth_wrong_text)
    else:
        city_list = rapid.get_city_list(search_res, message.text)
        if not city_list:
            logger.info('handlers.city - No result. '
                        'Process stopped!\n=================================================\n')
            bot.send_message(message.from_user.id, 'К сожалению, по данному названию ничего не найдено.'
                                                   '\n\n{help}'.format(help=loaders.help_text))
        else:
            markup = keyboards.custom_keyboard(city_list)
            bot.send_message(message.from_user.id, text='Выберите один вариант из предложенных:', reply_markup=markup)
            bot.register_next_step_handler(message, city_hotels, search_res, user)


@logger.catch
def city_hotels(message, search_res, user) -> None:
    """
    Функция получает id-города из результата запроса, определяет нужную строку запроса и подставляет в нее значение id.
    Запрашивает денежную единицу для подсчёта стоимости проживания с помощью клавиатуры.

    :param message:
    :param search_res:
    :param user:
    :type message: Message
    :type search_res: dict
    :type user: Users

    :return: None
    """
    user.city = message.text
    if user.command == '/lowprice':
        user.qu_s = loaders.lp
    elif user.command == '/highprice':
        user.qu_s = loaders.hp
    else:
        user.qu_s = loaders.bd
    user.qu_s['locale'] = 'ru_RU' if re.match(r'[А-Яа-яЁё]+', message.text) else 'en_US'
    city_ident = rapid.get_city_id(search_res, message.text)
    user.qu_s['destinationId'] = city_ident
    bot.send_message(
        message.from_user.id,
        text='Выберите денежную единицу для подсчета стоимости',
        reply_markup=keyboards.mark_currency
                     )
    if user.command == '/bestdeal':
        bot.register_next_step_handler(message, min_price, user)
    else:
        bot.register_next_step_handler(message, date_in, user)


@logger.catch
def min_price(message, user):
    """
    Функция запрашивает у пользователя минимальную стоимость за номер в отеле
    :param message:
    :param user:
    :type message: Message
    :type user: Users

    :return: None
    """
    user.currency = message.text
    user.qu_s['currency'] = message.text
    bot.send_message(message.from_user.id, 'Введите минимальную стоимость номера(не меньше 0):')
    bot.register_next_step_handler(message, max_price, user)


@logger.catch
def max_price(message, user):
    """
    Функция запрашивает у пользователя максимальную стоимость за номер в отеле
    :param message:
    :param user:
    :type message: Message
    :type user: Users

    :return: None
    """
    text_check = re.match(r'^\d+$', message.text)
    if not text_check:
        bot.send_message(message.from_user.id, 'Введите минимальную стоимость номера(не меньше 0)'
                                               '\nПожалуйста, целыми числами:')
        bot.register_next_step_handler(message, max_price, user)
    else:
        if int(message.text) < 0:
            bot.send_message(message.from_user.id, 'Введена стоимость меньше 0.'
                                                   '\nВведите минимальную стоимость номера(не меньше 0):')
            bot.register_next_step_handler(message, max_price, user)
        else:
            user.qu_s['priceMin'] = message.text
            user.min_price = int(message.text)
            bot.send_message(message.from_user.id, f'Минимальная стоимость номера: {user.min_price} '
                                                   f'{user.qu_s["currency"]}.'
                                                   f'\nВведите максимальную стоимость номера:')
            bot.register_next_step_handler(message, min_distance, user)


@logger.catch
def min_distance(message, user):
    """
    Функция запрашивает у пользователя минимальное расстояние до центра города
    :param message:
    :param user:
    :type message: Message
    :type user: Users

    :return: None
    """
    text_check = re.match(r'^\d+$', message.text)
    if not text_check:
        bot.send_message(message.from_user.id, f'Минимальная стоимость номера: {user.min_price} '
                                               f'{user.qu_s["currency"]}.'
                                               f'\nВведите максимальную стоимость номера\nПожалуйста, цифрами:')
        bot.register_next_step_handler(message, min_distance, user)
    else:
        if int(message.text) <= user.min_price:
            bot.send_message(message.from_user.id, f'Максимальная стоимость не может быть меньше минимальной.'
                                                   f'\nМинимальная стоимость номера: {user.min_price} '
                                                   f'{user.qu_s["currency"]}.'
                                                   f'\nВведите максимальную стоимость номера:')
            bot.register_next_step_handler(message, min_distance, user)
        else:
            user.qu_s['priceMax'] = message.text
            user.max_price = int(message.text)
            bot.send_message(message.from_user.id, 'Введите минимальное расстояние от центра города(км) '
                                                   'целым числом или в формате "0.5":')
            bot.register_next_step_handler(message, max_distance, user)


@logger.catch
def max_distance(message, user):
    """
    Функция запрашивает у пользователя максимальное расстояние до центра города
    :param message:
    :param user:
    :type message: Message
    :type user: Users

    :return: None
    """
    text_check = re.match(r'^\d+$', message.text)
    text_check2 = re.match(r'^\d+\.\d+$', message.text)
    if not text_check and not text_check2:
        bot.send_message(message.from_user.id, 'Неподходящий формат записи.'
                                               '\nВведите минимальное расстояние от центра города(км) '
                                               'целым числом или в формате "0.5":')
        bot.register_next_step_handler(message, max_distance, user)
    else:
        if float(message.text) < 0:
            bot.send_message(message.from_user.id, 'Расстояние не может быть меньше 0.'
                                                   '\nВведите минимальное расстояние от центра города(км) '
                                                   'целым числом или в формате "0.5":')
            bot.register_next_step_handler(message, max_distance, user)

        else:
            user.min_distance = float(message.text)
            bot.send_message(message.from_user.id, f'Минимальное расстояние: {user.min_distance}.'
                                                   f'\nВведите максимальное расстояние от центра города(км) '
                                                   f'целым числом или в формате "0.5":')
            bot.register_next_step_handler(message, date_in, user)


@logger.catch
def date_in(message, user):
    """
    Функция запрашивает дату заезда с помощью календаря.
    :param message:
    :param user:
    :type message: Message
    :type user: Users

    :return: None
    """
    if user.command == '/bestdeal':
        text_check = re.match(r'^\d+$', message.text)
        text_check2 = re.match(r'^\d+\.\d+$', message.text)
        if not text_check and not text_check2:
            bot.send_message(message.from_user.id, f'Неподходящий формат записи.'
                                                   f'\nМинимальное расстояние: {user.min_distance}.'
                                                   f'\nВведите максимальное расстояние от центра города(км) '
                                                   f'целым числом или в формате "0.5":')
            bot.register_next_step_handler(message, date_in, user)
        else:
            if float(message.text) <= user.min_distance:
                bot.send_message(message.from_user.id, f'Максимальное расстояние не может быть меньше минимального.'
                                                       f'\nМинимальное расстояние: {user.min_distance}.'
                                                       f'\nВведите максимальное расстояние от центра города '
                                                       f'целым числом или в формате "0.5":')
                bot.register_next_step_handler(message, date_in, user)
            else:
                user.max_distance = float(message.text)
    else:
        user.qu_s['currency'] = message.text
    bot.send_message(message.from_user.id,
                     'Выберите дату заселения',
                     reply_markup=calendar.create_calendar(
                         name=calendar_in.prefix,
                         year=now.year,
                         month=now.month)
                     )


@logger.catch
def num_photos(message, user) -> None:
    """
    Функция сохраняет необходимое количество отелей.
    Запрашивает необходимое количество фотографий отелей,
    которые нужно показать (не более 3, можно отказаться от загрузки фото).

    :param message:
    :param user:
    :type message: Message
    :type user: Users

    :return: None
    """
    hotels_n = int(message.text)
    user.qu_s['checkIn'] = user.check_in
    user.qu_s['checkOut'] = user.check_out
    bot.send_message(message.from_user.id,
                     text='Сколько фотографий показать для каждого отеля?',
                     reply_markup=keyboards.photos_num
                     )
    bot.register_next_step_handler(message, show_hotels, hotels_n, user)


@logger.catch
def show_hotels(message, hotels_n, user) -> None:
    """
    Функция проверяет количество фотографий, необходимое к загрузке и
    формирует на основе собранной из API информации ответ для пользователя.
    Отправляет результаты поиска пользователю.

    :param message:
    :param hotels_n:
    :param user:
    :type message: Message
    :type hotels_n: int
    :type user: Users

    :return: None
    """
    logger.info('handlers.show_hotels - Query parameters:\n     Selected city: {city}'
                '\n     Price range: {min_p}-{max_p}\n     Distance range: {min_d}-{max_d} km'
                '\n     Check in-out: {ch_in} - {ch_out}\n     Number od hotels: {hot_n}\n     Photos flag: {ph_f}'.
                format(city=user.city, min_p=user.min_price, max_p=user.max_price, min_d=user.min_distance,
                       max_d=user.max_distance, ch_in=user.check_in, ch_out=user.check_out,
                       hot_n=hotels_n, ph_f=message.text))
    hotels_dct = rapid.get_rapid_json(user.qu_s, loaders.get_hotels_url, hotels_control_pat)
    if hotels_dct == {'result': 'timeout'}:
        logger.info('handlers.show_hotels - ReadTimeout.'
                    ' Process stopped!\n=================================================\n')
        bot.send_message(message.from_user.id, loaders.timeout_error_text)
    elif hotels_dct == {'result': 'error'}:
        logger.info('handlers.show_hotels - Error!'
                    ' Process stopped!\n=================================================\n')
        bot.send_message(message.from_user.id, loaders.smth_wrong_text)
    else:
        if user.command == '/bestdeal':
            hotels_list = rapid.get_hotels(hotels_n, hotels_dct, user.min_distance, user.max_distance)
        else:
            hotels_list = rapid.get_hotels(hotels_n, hotels_dct)

        if not hotels_list:
            bot.send_message(message.from_user.id, 'К сожалению отелей, удовлетворяющих запросу не найдено.')
            logger.info('handlers.show_hotels - No result.'
                        ' Process stopped!\n=================================================\n')
            bot.send_message(message.from_user.id, loaders.help_text)
        elif message.text == 'Не показывать':
            text_list = list()
            for i_hotel in hotels_list:
                hot_text = 'Название:\n    {name}\n' \
                           'Адрес:\n    {address}\n' \
                           'Расстояние до центра:\n    {c_center}\n' \
                           'Цена за время пребывания:\n   {current}'.format(name=i_hotel['name'],
                                                                            address=i_hotel['address'],
                                                                            c_center=i_hotel['c_center'],
                                                                            current=i_hotel['current']
                                                                            )
                text_list.append(hot_text)
                bot.send_message(message.from_user.id, hot_text)
            js_hotels_list = json.dumps(text_list)
            with db:
                db_user = User.create(u_id=message.from_user.id,
                                      command=user.command,
                                      date=user.date,
                                      city=user.city,
                                      currency=user.currency,
                                      check_in=user.check_in,
                                      check_out=user.check_out,
                                      min_price=user.min_price,
                                      max_price=user.max_price,
                                      min_distance=user.min_distance,
                                      max_distance=user.max_distance,
                                      photos_check=user.photos_check,
                                      hotels=js_hotels_list)
                db_user.save()
            logger.info('handlers.show_hotels -'
                        ' Command completed!\n=================================================\n')
            bot.send_message(message.from_user.id, loaders.help_text, reply_markup=ReplyKeyboardRemove())
        else:
            media_list = list()
            text_list = list()
            user.photos_check = True
            photos_n = int(message.text)
            for i_hotel in hotels_list:
                qs = {'id': i_hotel['id']}
                photos_dct = rapid.get_rapid_json(qs, loaders.get_photos_url, photos_control_pat)
                if photos_dct == {'result': 'timeout'}:
                    logger.info('handlers.show_hotels - ReadTimeout.'
                                ' Process stopped!\n=================================================\n')
                    bot.send_message(message.from_user.id, loaders.timeout_error_text)
                elif photos_dct == {'result': 'error'}:
                    logger.info('handlers.show_hotels - Error!'
                                ' Process stopped!\n=================================================\n')
                    bot.send_message(message.from_user.id, loaders.smth_wrong_text)
                else:
                    if photos_n > 5:
                        photos_n = 5
                    photos = list()
                    hot_text = 'Название:\n    {name}\n' \
                               'Адрес:\n    {address}\n' \
                               'Расстояние до центра:\n    {c_center}\n'\
                               'Цена за время пребывания:\n   {current}'.format(name=i_hotel['name'],
                                                                                address=i_hotel['address'],
                                                                                c_center=i_hotel['c_center'],
                                                                                current=i_hotel['current']
                                                                                )
                    text_list.append(hot_text)
                    p_lst = rapid.get_photos_lst(photos_dct, photos_n)
                    media_list.append(p_lst)
                    for i_p_ind in range(photos_n):
                        for i_ind, i_photo in enumerate(p_lst):
                            if i_p_ind == i_ind:
                                if i_p_ind == 0:
                                    photos.append(InputMediaPhoto(i_photo, caption=hot_text))
                                else:
                                    photos.append(InputMediaPhoto(i_photo))
                    bot.send_media_group(message.from_user.id, photos)
            ml_json = json.dumps(media_list)
            tl_json = json.dumps(text_list)
            with db:
                db_user = User.create(u_id=message.from_user.id,
                                      command=user.command,
                                      date=user.date,
                                      city=user.city,
                                      currency=user.currency,
                                      check_in=user.check_in,
                                      check_out=user.check_out,
                                      min_price=user.min_price,
                                      max_price=user.max_price,
                                      min_distance=user.min_distance,
                                      max_distance=user.max_distance,
                                      photos_check=user.photos_check,
                                      photos_list=ml_json,
                                      hotels=tl_json)
                db_user.save()
            logger.info('handlers.show_hotels -'
                        ' Command completed!\n=================================================\n')
            bot.send_message(message.from_user.id, loaders.help_text, reply_markup=ReplyKeyboardRemove())
