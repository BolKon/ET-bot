import requests
import json
import handlers
import re
from telebot.types import InputMediaPhoto


def search_city(querystring) -> dict:
    """
    Функция получает json-файл со списком городов по названию и возвращает его в виде словаря

    :param querystring:
    :type querystring: dict

    :return: se_res
    :rtype: dict
    """
    url = handlers.get_city_url

    s_headers = handlers.site_header

    response = requests.request("GET", url, headers=s_headers, params=querystring)

    se_res = json.loads(response.text)
    return se_res


def get_city_list(city_dct, city_name) -> list:
    """
    Функция возвращает уточняющий список городов с совпадающим названием из запроса

    :param city_dct:
    :param city_name:
    :type city_dct: dict
    :type city_name: str

    :return: city_list
    :rtype: list
    """
    city_list = []
    for i_elem in city_dct['suggestions']:
        if i_elem['group'] == 'CITY_GROUP':
            for i_var in i_elem['entities']:
                if i_var['name'].lower() == city_name.lower():
                    city_list.append(c_highlighter(i_var['caption']))
            return city_list


def get_city_id(city_dct, city_name) -> str:
    """
    Функция возвращает id города после его уточнения

    :param city_dct:
    :param city_name:
    :type city_dct: dict
    :type city_name: str

    :return: city_id
    :rtype: str
    """
    for i_elem in city_dct['suggestions']:
        if i_elem['group'] == 'CITY_GROUP':
            for i_var in i_elem['entities']:
                if c_highlighter(i_var['caption']) == city_name:
                    city_id = i_var['destinationId']
                    return city_id


def c_highlighter(text) -> str:
    """
    Функция убирает разметку из строки с описанием названия города

    :param text:
    :type text: str

    :return: result
    :rtype: str
    """
    result = re.findall(r"<span class='highlighted'>(\w+)", text) + re.findall(r"</span>, (.+)", text)
    result = ', '.join(result)
    return result


def get_hotels_dict(querystring) -> dict:
    """
    Функция получает json-файл со списком отелей в выбранном городе и возвращает его в виде словаря

    :param querystring:
    :type querystring: dict

    :return: hotels_dct
    :rtype: dict
    """
    url = handlers.get_hotels_url

    s_headers = handlers.site_header

    response = requests.request("GET", url, headers=s_headers, params=querystring)
    hotels_dct = json.loads(response.text)
    return hotels_dct


def get_hotels(h_num, hotels_dct) -> list:
    """
    Функция формирует список с заданным количеством словарей, содержащих информацию об отелях

    :param h_num:
    :param hotels_dct:
    :type h_num: int
    :type hotels_dct: dict

    :return: hotels_list
    :rtype: list
    """
    hotels_list = []
    for i_hot in range(h_num):
        for i_ind, i_elem in enumerate(hotels_dct['data']['body']['searchResults']['results']):
            if i_ind == i_hot:
                hotel = dict()

                hotel['id'] = str(i_elem['id'])
                hotel['name'] = i_elem['name']

                if 'streetAddress' in i_elem['address']:
                    hotel['address'] = i_elem['address']['streetAddress']
                else:
                    hotel['address'] = 'Не указан'

                hotel['c_center'] = 'Нет данных'
                for i_lab in i_elem['landmarks']:
                    if i_lab['label'] == 'City center':
                        hotel['c_center'] = i_lab['distance']

                hotel['current'] = i_elem['ratePlan']['price']['current']
                hotels_list.append(hotel)

    return hotels_list


def get_photos(querystring) -> dict:
    """
    Функция получает json-файл со ссылками на фотографии данного отеля и возвращает его в виде словаря

    :param querystring:
    :type querystring: dict

    :return: photos_dct
    :rtype: dict
    """
    url = handlers.get_photos_url

    s_headers = handlers.site_header

    response = requests.request("GET", url, headers=s_headers, params=querystring)

    photos_dct = json.loads(response.text)

    return photos_dct


def get_photos_lst(photos_dct, photos_n, hot_text) -> list:
    """
    Функция формирует медиа-группу из фотографий отеля, добавляя к первому элементу текстовое описание этого отеля

    :param photos_dct:
    :param photos_n:
    :param hot_text:
    :type photos_dct: dict
    :type photos_n: int
    :type hot_text: str

    :return: photos_lst
    :rtype: list
    """
    photos_lst = list()
    for i_ph in range(photos_n):
        for i_ind, i_photo in enumerate(photos_dct['hotelImages']):
            if i_ind == i_ph:
                if i_ph == 0:
                    photos_lst.append(InputMediaPhoto(i_photo['baseUrl'].format(size='w'), caption=hot_text))
                else:
                    photos_lst.append(InputMediaPhoto(i_photo['baseUrl'].format(size='w')))

    return photos_lst
