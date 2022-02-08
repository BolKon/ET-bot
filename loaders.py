import os
import datetime
import telebot
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
        self.hotels = None

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


now = datetime.datetime.now()


get_city_url = 'https://hotels4.p.rapidapi.com/locations/v2/search'
get_hotels_url = "https://hotels4.p.rapidapi.com/properties/list"
get_photos_url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

lp = {"destinationId": "1137639", "pageNumber": "1", "pageSize": "25", "checkIn": "2022-02-15",
      "checkOut": "2022-02-21", "adults1": "1", "sortOrder": "PRICE", "locale": "ru_RU", "currency": "RUB"}

hp = {"destinationId": "1137639", "pageNumber": "1", "pageSize": "25", "checkIn": "2022-02-15",
      "checkOut": "2022-02-21", "adults1": "1", "sortOrder": "PRICE_HIGHEST_FIRST", "locale": "ru_RU",
      "currency": "RUB"}

bd = {}

city_control_pat = r'(?<="CITY_GROUP",).+?[\]]'
hotels_control_pat = r'(?<="results": \[).+?"pagination"'   #не работает
photos_control_pat = r'"hotelImages": \['                   #пока неизвестно (думаю, что тоже не работает)

search_city = {"query": "new york", "locale": "ru_RU", "currency": "USD"}

search_hotel = {"destinationId": "1506246", "pageNumber": "1", "pageSize": "25", "checkIn":"2020-01-08",
                "checkOut": "2020-01-15", "adults1": "1", "sortOrder": "PRICE", "locale": "en_US", "currency": "USD"}

site_header = {'x-rapidapi-host': "hotels4.p.rapidapi.com",
               'x-rapidapi-key': os.getenv('SITE_LOG')
               }