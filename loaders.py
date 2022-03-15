import os
import datetime
import telebot
from loguru import logger
from dotenv import load_dotenv


load_dotenv('.env')
token = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(token)


class Users:
    users = dict()

    def __init__(self, user_id):
        self.city = None
        self.check_in = None
        self.check_out = None
        self.command = None
        self.date = None
        self.currency = None
        self.min_price = None
        self.max_price = None
        self.min_distance = None
        self.max_distance = None
        self.qu_s = None
        self.photos_check = False

        Users.add_user(user_id, self)

    @staticmethod
    def get_user(user_id):
        if Users.users.get(user_id) is None:
            new_user = Users(user_id)
            return new_user
        return Users.users.get(user_id)

    @classmethod
    def add_user(cls, user_id, user):
        cls.users[user_id] = user


def info_only(record):
    return record["level"].name == "INFO"


bot_logger = logger
bot_logger.add('info.log', format='{time} {message}', level='INFO', rotation='10 MB',
               compression='zip', filter=info_only)
bot_logger.add('debug.log', format='{time} {message}', level='ERROR', rotation='10 MB', compression='zip')

now = datetime.datetime.now()


help_text = 'Доступные команды:\n /lowprice - поиск самых дешёвых отелей в городе\n ' \
            '/highprice - поиск самых дорогих отелей в городе\n '\
            '/bestdeal - поиск отелей наиболее подходящих по цене '\
            'и удалённости от центра города\n '\
            '/history - вывод истории поиска отелей'

timeout_error_text = 'Превышено время ожидания ответа.\n   ' \
                     'Пожалуйста, повторите запрос.\n\n{help}'.format(help=help_text)
smth_wrong_text = 'Ой! Что-то пошло не так.\n   Пожалуйста повторите запрос.\n\n{help}'.format(help=help_text)

get_city_url = 'https://hotels4.p.rapidapi.com/locations/v2/search'
get_hotels_url = "https://hotels4.p.rapidapi.com/properties/list"
get_photos_url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

lp = {"destinationId": "1137639", "pageNumber": "1", "pageSize": "10", "checkIn": "2022-02-15",
      "checkOut": "2022-02-21", "adults1": "1", "sortOrder": "PRICE", "locale": "ru_RU", "currency": "RUB"}

hp = {"destinationId": "1137639", "pageNumber": "1", "pageSize": "10", "checkIn": "2022-02-15",
      "checkOut": "2022-02-21", "adults1": "1", "sortOrder": "PRICE_HIGHEST_FIRST", "locale": "ru_RU",
      "currency": "RUB"}

bd = {"destinationId": "1506246", "pageNumber": "1", "pageSize": "10", "checkIn": "2020-01-08",
      "checkOut": "2020-01-15", "adults1": "1", "priceMin": "300", "priceMax": "2000",
      "sortOrder": "DISTANCE_FROM_LANDMARK", "locale": "ru_RU", "currency": "RUB"}

city_control_pat = r'(?<="CITY_GROUP",).+?[\]]'
hotels_control_pat = r'(?<=,)"results":.+?(?=,"pagination")'
photos_control_pat = r'(?<=,)"hotelImages":.+?(?="roomImages":)'

search_city = {"query": "new york", "locale": "ru_RU"}

search_hotel = {"destinationId": "1506246", "pageNumber": "1", "pageSize": "25", "checkIn": "2020-01-08",
                "checkOut": "2020-01-15", "adults1": "1", "sortOrder": "PRICE", "locale": "en_US", "currency": "USD"}

site_header = {'x-rapidapi-host': "hotels4.p.rapidapi.com",
               'x-rapidapi-key': os.getenv('SITE_LOG')
               }

rand_answer = ('Извини, котик, но я не говорю на кошачьем\U0001F408 \U0001F43E',
               'Я Вас понял, но нет!\U0001F604', 'Искать меня научили, а вот, читать, нет\U0001F605')
