import loaders
import re
import rapid
import keyboards
from loaders import bot, now, Users, city_control_pat, hotels_control_pat, photos_control_pat
from keyboards import calendar, calendar_in


qu = dict()


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
    search_res = rapid.get_rapid_json(se_ci, loaders.get_city_url, city_control_pat)
    if search_res == {'result': 'timeout'}:
        bot.send_message(message.from_user.id, loaders.timeout_error_text)
    elif search_res == {'result': 'error'}:
        bot.send_message(message.from_user.id, loaders.smth_wrong_text)
    else:
        city_list = rapid.get_city_list(search_res, message.text)
        if not city_list:
            bot.send_message(message.from_user.id, 'К сожалению, по данному названию ничего не найдено.'
                                                   '\n\n{help}'.format(help=loaders.help_text))
        else:
            markup = keyboards.custom_keyboard(city_list)
            bot.send_message(message.from_user.id, text='Выберите один вариант из предложенных:', reply_markup=markup)
            bot.register_next_step_handler(message, city_hotels, search_res, user)


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
    global qu
    user.city = message.text
    if user.command == '/lowprice':
        qu = loaders.lp
    elif user.command == '/highprice':
        qu = loaders.hp
    else:
        qu = loaders.bd
    qu['locale'] = 'ru_RU' if re.match(r'[А-Яа-яЁё]+', message.text) else 'en_US'
    city_ident = rapid.get_city_id(search_res, message.text)
    qu['destinationId'] = city_ident
    bot.send_message(
        message.from_user.id,
        text='Выберите денежную единицу для подсчета стоимости',
        reply_markup=keyboards.mark_currency
                     )
    if user.command == '/bestdeal':
        bot.register_next_step_handler(message, min_price, user)
    else:
        bot.register_next_step_handler(message, date_in, user)


def min_price(message, user):
    """
    Функция запрашивает у пользователя минимальную стоимость за номер в отеле
    :param message:
    :param user:
    :return:
    """
    qu['currency'] = message.text
    bot.send_message(message.from_user.id, 'Введите минимальную стоимость номера(не меньше 0):')
    bot.register_next_step_handler(message, max_price, user)


def max_price(message, user):
    """
    Функция запрашивает у пользователя максимальную стоимость за номер в отеле
    :param message:
    :param user:
    :return:
    """
    text_check = re.match(r'^\d+$', message.text)
    if not text_check:
        bot.send_message(message.from_user.id, 'Введите минимальную стоимость номера(не меньше 0)'
                                               '\nПожалуйста, цифрами:')
        bot.register_next_step_handler(message, max_price, user)
    else:
        if int(message.text) < 0:
            bot.send_message(message.from_user.id, 'Введена стоимость меньше 0.'
                                                   '\nВведите минимальную стоимость номера(не меньше 0):')
            bot.register_next_step_handler(message, max_price, user)
        else:
            qu['priceMin'] = message.text
            user.min_price = int(message.text)
            bot.send_message(message.from_user.id, f'Минимальная стоимость номера: {user.min_price}{qu["currency"]}.'
                                                   f'\nВведите максимальную стоимость номера:')
            bot.register_next_step_handler(message, min_distance, user)


def min_distance(message, user):
    """
    Функция запрашивает у пользователя минимальное расстояние до центра города
    :param message:
    :param user:
    :return:
    """
    text_check = re.match(r'^\d+$', message.text)
    if not text_check:
        bot.send_message(message.from_user.id, f'Минимальная стоимость номера: {user.min_price}{qu["currency"]}.'
                                               f'\nВведите максимальную стоимость номера\nПожалуйста, цифрами:')
        bot.register_next_step_handler(message, min_distance, user)
    else:
        if int(message.text) <= user.min_price:
            bot.send_message(message.from_user.id, f'Максимальная стоимость не может быть меньше минимальной.'
                                                   f'\nМинимальная стоимость номера: {user.min_price}{qu["currency"]}.'
                                                   f'\nВведите максимальную стоимость номера:')
            bot.register_next_step_handler(message, min_distance, user)
        else:
            qu['priceMax'] = message.text
            bot.send_message(message.from_user.id, 'Введите минимальное расстояние от центра города '
                                                   'целым числом или в формате "0.5":')
            bot.register_next_step_handler(message, max_distance, user)


def max_distance(message, user):
    """
    Функция запрашивает у пользователя максимальное расстояние до центра города
    :param message:
    :param user:
    :return:
    """
    text_check = re.match(r'^\d+$', message.text)
    text_check2 = re.match(r'^\d+\.\d+$', message.text)
    if not text_check and not text_check2:
        bot.send_message(message.from_user.id, 'Неподходящий формат записи.'
                                               '\nВведите минимальное расстояние от центра города '
                                               'целым числом или в формате "0.5":')
        bot.register_next_step_handler(message, max_distance, user)
    else:
        if float(message.text) < 0:
            bot.send_message(message.from_user.id, 'Расстояние не может быть меньше 0.'
                                                   '\nВведите минимальное расстояние от центра города '
                                                   'целым числом или в формате "0.5":')
            bot.register_next_step_handler(message, max_distance, user)

        else:
            user.min_distance = float(message.text)
            bot.send_message(message.from_user.id, f'Минимальное расстояние: {user.min_distance}.'
                                                   f'\nВведите максимальное расстояние от центра города '
                                                   f'целым числом или в формате "0.5":')
            bot.register_next_step_handler(message, date_in, user)


def date_in(message, user):
    """
    Функция запрашивает дату заезда с помощью календаря.
    :param message:
    :param user:
    :type message: Message
    :type user: Users

    :return:
    """
    if user.command == '/bestdeal':
        text_check = re.match(r'^\d+$', message.text)
        text_check2 = re.match(r'^\d+\.\d+$', message.text)
        if not text_check and not text_check2:
            bot.send_message(message.from_user.id, f'Неподходящий формат записи.'
                                                   f'\nМинимальное расстояние: {user.min_distance}.'
                                                   f'\nВведите максимальное расстояние от центра города '
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
        qu['currency'] = message.text
    bot.send_message(message.from_user.id,
                     'Выберите дату заезда',
                     reply_markup=calendar.create_calendar(
                         name=calendar_in.prefix,
                         year=now.year,
                         month=now.month)
                     )


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
    global qu
    hotels_n = int(message.text)
    qu['checkIn'] = user.check_in
    qu['checkOut'] = user.check_out
    bot.send_message(message.from_user.id,
                     text='Сколько фотографий отелей показать?',
                     reply_markup=keyboards.photos_num
                     )
    bot.register_next_step_handler(message, show_hotels, hotels_n, user)


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
    hotels_dct = rapid.get_rapid_json(qu, loaders.get_hotels_url, hotels_control_pat)
    if hotels_dct == {'result': 'timeout'}:
        bot.send_message(message.from_user.id, loaders.timeout_error_text)
    elif hotels_dct == {'result': 'error'}:
        bot.send_message(message.from_user.id, loaders.smth_wrong_text)
    else:
        if user.command == '/bestdeal':
            hotels_list = rapid.get_hotels(hotels_n, hotels_dct, user.min_distance, user.max_distance)
        else:
            hotels_list = rapid.get_hotels(hotels_n, hotels_dct)

        if not hotels_list:
            bot.send_message(message.from_user.id, 'К сожалению отелей, удовлетворяющих запросу не найдено.')
            bot.send_message(message.from_user.id, loaders.help_text)
        elif message.text == 'Не показывать':
            user.hotels = hotels_list
            for i_hotel in hotels_list:
                bot.send_message(message.from_user.id, 'Название:\n    {name}\n'
                                                       'Адрес:\n    {address}\n'
                                                       'Расстояние до центра:\n    {c_center}\n'
                                                       'Цена за время пребывания:\n    '
                                                       '{current}'.format(name=i_hotel['name'],
                                                                          address=i_hotel['address'],
                                                                          c_center=i_hotel['c_center'],
                                                                          current=i_hotel['current']
                                                                          )
                                     )
                bot.send_message(message.from_user.id, loaders.help_text)
        else:
            hot_list = list()
            photos_n = int(message.text)
            for i_hotel in hotels_list:
                qs = {'id': i_hotel['id']}
                photos_dct = rapid.get_rapid_json(qs, loaders.get_photos_url, photos_control_pat)
                if photos_dct == {'result': 'timeout'}:
                    bot.send_message(message.from_user.id, loaders.timeout_error_text)
                elif photos_dct == {'result': 'error'}:
                    bot.send_message(message.from_user.id, loaders.smth_wrong_text)
                else:
                    hot_text = 'Название:\n    {name}\n' \
                               'Адрес:\n    {address}\n' \
                               'Расстояние до центра:\n    {c_center}\n'\
                               'Цена за время пребывания:\n   {current}'.format(name=i_hotel['name'],
                                                                                address=i_hotel['address'],
                                                                                c_center=i_hotel['c_center'],
                                                                                current=i_hotel['current']
                                                                                )
                    p_lst = rapid.get_photos_lst(photos_dct, photos_n, hot_text)
                    hot_list.append(p_lst)
                    bot.send_media_group(message.from_user.id, p_lst)
                user.hotels = hot_list
            bot.send_message(message.from_user.id, loaders.help_text)
