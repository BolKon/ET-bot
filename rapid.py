import requests
import json
import re
import loaders
from loguru import logger
from requests.exceptions import ReadTimeout
from requests.exceptions import HTTPError


def get_rapid_json(querystring, url, control_pat):
    """
    Функция получает json-файл по заданной строке запроса и url и возвращает его в виде словаря

    :param querystring:
    :param url:
    :param control_pat:
    :type querystring: dict
    :type url: str
    :type control_pat: str

    :return: se_res
    :rtype: dict
    """

    s_headers = loaders.site_header
    try:
        response = requests.request("GET", url, headers=s_headers, params=querystring, timeout=10)
        if response.status_code == requests.codes.ok:
            find = re.search(control_pat, response.text)
            if find:
                se_res = json.loads(response.text)
                return se_res
            else:
                raise ValueError('No search result!')
        else:
            response.raise_for_status()
    except ReadTimeout as er:
        logger.error(f'rapid.get_rapid_json - {er}\n=================================================\n')
        se_res = {'result': 'timeout'}
        return se_res
    except HTTPError as er:
        logger.error(f'rapid.get_rapid_json - {er}\n=================================================\n')
        se_res = {'result': 'error'}
        return se_res
    except ValueError as er:
        logger.error(f'rapid.get_rapid_json - {er}\n=================================================\n')
        se_res = {'result': 'error'}
        return se_res


@logger.catch
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


@logger.catch
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


@logger.catch
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


@logger.catch
def get_hotels(h_num, hotels_dct, min_dist=0, max_dist=1000) -> list:
    """
    Функция формирует список с заданным количеством словарей, содержащих информацию об отелях

    :param h_num:
    :param hotels_dct:
    :param min_dist
    :param max_dist
    :type h_num: int
    :type hotels_dct: dict
    :type min_dist: int
    :type max_dist: int

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
                    if i_lab['label'] in ('City center', 'Центр города'):
                        hotel['c_center'] = i_lab['distance']

                if hotel['c_center'] != 'Нет данных':
                    c_dist_str = re.sub(r',', '.', hotel['c_center'])
                    c_dist = float(re.sub(r' км', '', c_dist_str))
                    if min_dist <= c_dist <= max_dist:
                        hotel['current'] = i_elem['ratePlan']['price']['current']
                        hotels_list.append(hotel)
    return hotels_list


@logger.catch
def get_photos_lst(photos_dct, photos_n) -> list:
    """
    Функция формирует список из фотографий отеля

    :param photos_dct:
    :param photos_n:
    :type photos_dct: dict
    :type photos_n: int

    :return: photos_lst
    :rtype: list
    """
    photos_lst = list()
    for i_ph in range(photos_n):
        for i_ind, i_photo in enumerate(photos_dct['hotelImages']):
            if i_ind == i_ph:
                photos_lst.append(i_photo['baseUrl'].format(size='w'))

    return photos_lst
