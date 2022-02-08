import loaders
import re
import rapid
import keyboards
from loaders import bot, now, Users, city_control_pat, hotels_control_pat, photos_control_pat
from keyboards import calendar, calendar_in


def city(message, user) -> None:
    """
    Функция получает результат поиска города через API сайта
    и формирует из полученных результатов клавиатуру для более точного определения города для поиска отеля.
    Может определить на каком языке (русский или английский) делался запрос для выдачи более корректного результата.
    :param message:
    :param user:
    :type user: Users

    :return: None
    """
    se_ci = loaders.search_city
    se_ci['locale'] = 'ru_RU' if re.match(r'[А-Яа-яЁё]+', message.text) else 'en_US'
    se_ci['query'] = message.text
    search_res = rapid.get_rapid_json(se_ci, loaders.get_city_url, city_control_pat)
    city_list = rapid.get_city_list(search_res, message.text)
    if not city_list:
        bot.send_message(message.from_user.id, 'К сожалению по данному названию ничего не найдено.\n'
                                               '  Попробуйте начать сначала. /help')
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
    :type search_res: dict
    :type user: Users

    :return: None
    """
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
    bot.register_next_step_handler(message, date_in, qu, user)


def date_in(message, qu, user):
    """
    Функция запрашивает дату заезда с помощью календаря.
    :param message:
    :param qu:
    :param user:
    :type qu: dict
    :type user: Users

    :return:
    """
    qu['currency'] = message.text
    bot.send_message(message.from_user.id,
                     'Выберите дату заезда',
                     reply_markup=calendar.create_calendar(
                         name=calendar_in.prefix,
                         year=now.year,
                         month=now.month)
                     )
    bot.register_next_step_handler(message, date_out, qu, user)


def date_out(message, qu, user):
    """
    Функция запрашивает дату выезда с помощью календаря.
    :param message:
    :param qu:
    :param user:
    :type qu: dict
    :type user: Users

    :return:
    """
    qu['checkIn'] = message.text
    user.check_in = message.text
    bot.send_message(message.from_user.id,
                     'Выберите дату выезда',
                     reply_markup=calendar.create_calendar(
                         name=calendar_in.prefix,
                         year=now.year,
                         month=now.month
                     )
                     )
    bot.register_next_step_handler(message, hotels_number, qu, user)


def hotels_number(message, qu, user) -> None:
    """
    Функция применяет выбранное значение денежной единицы к строке запроса.
    Запрашивает у пользователя информацию о скольки отелях необходимо показать с помощью клавиатуры (не более 3).

    :param message:
    :param qu:
    :param user:
    :type qu: dict
    :type user: Users

    :return: None
    """
    qu['checkOut'] = message.text
    user.check_out = message.text
    bot.send_message(message.from_user.id, text='Сколько отелей показать?', reply_markup=keyboards.hotels_num)
    bot.register_next_step_handler(message, num_photos, qu, user)


def num_photos(message, qu, user) -> None:
    """
    Функция сохраняет необходимое количество отелей.
    Запрашивает необходимое количество фотографий отелей,
    которые нужно показать (не более 3, можно отказаться от загрузки фото).

    :param message:
    :param qu:
    :param user:
    :type qu: dict
    :type user: Users

    :return: None
    """
    hotels_n = int(message.text)
    bot.send_message(message.from_user.id,
                     text='Сколько фотографий отелей показать?',
                     reply_markup=keyboards.photos_num
                     )
    bot.register_next_step_handler(message, show_hotels, qu, hotels_n, user)


def show_hotels(message, qu, hotels_n, user) -> None:
    """
    Функция проверяет количество фотографий, необходимое к загрузке и
    формирует на основе собранной из API информации ответ для пользователя.
    Отправляет результаты поиска пользователю.

    :param message:
    :param qu:
    :param hotels_n:
    :param user:
    :type qu: dict
    :type hotels_n: int
    :type user: Users

    :return: None
    """
    hotels_dct = rapid.get_rapid_json(qu, loaders.get_hotels_url, hotels_control_pat)
    hotels_list = rapid.get_hotels(hotels_n, hotels_dct)
    if message.text == 'Не показывать':
        user.hotels = hotels_list
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
        hot_list = list()
        photos_n = int(message.text)
        for i_hotel in hotels_list:
            qs = {'id': i_hotel['id']}
            p_dct = rapid.get_rapid_json(qs, loaders.get_photos_url, photos_control_pat)
            hot_text = 'Название:\n    {name}\n' \
                       'Адрес:\n    {address}\n' \
                       'Расстояние до центра:\n    {c_center}\n'\
                       'Цена за сутки:\n   {current}'.format(name=i_hotel['name'],
                                                             address=i_hotel['address'],
                                                             c_center=i_hotel['c_center'],
                                                             current=i_hotel['current']
                                                             )
            p_lst = rapid.get_photos_lst(p_dct, photos_n, hot_text)
            hot_list.append(p_lst)
            bot.send_media_group(message.from_user.id, p_lst)
        user.hotels = hot_list
