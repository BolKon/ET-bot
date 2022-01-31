import os
from dotenv import load_dotenv

load_dotenv('.env')

get_city_url = 'https://hotels4.p.rapidapi.com/locations/v2/search'
get_hotels_url = "https://hotels4.p.rapidapi.com/properties/list"
get_photos_url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

lp = {"destinationId": "1137639", "pageNumber": "1", "pageSize": "25", "checkIn": "2022-02-15",
      "checkOut": "2022-02-21", "adults1": "1", "sortOrder": "PRICE", "locale": "en_US", "currency": "RUB"}

hp = {"destinationId": "1137639", "pageNumber": "1", "pageSize": "25", "checkIn": "2022-02-15",
      "checkOut": "2022-02-21", "adults1": "1", "sortOrder": "PRICE_HIGHEST_FIRST", "locale": "en_US",
      "currency": "RUB"}

bd = {}

search_city = {"query": "new york", "locale": "en_US", "currency": "USD"}

search_hotel = {"destinationId": "1506246", "pageNumber": "1", "pageSize": "25", "checkIn":"2020-01-08",
                "checkOut": "2020-01-15", "adults1": "1", "sortOrder": "PRICE", "locale": "en_US", "currency": "USD"}

site_header = {'x-rapidapi-host': "hotels4.p.rapidapi.com",
               'x-rapidapi-key': os.getenv('SITE_LOG')
               }
