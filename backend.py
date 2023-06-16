from pprint import pprint
from datetime import datetime
# импорт библиотек 
import vk_api 
from vk_api.exceptions import ApiError
from config import acces_token
from data_base import *

# получение данных о пользователе


class VkTools:

    
    def __init__(self, acces_token):

        self.vkapi = vk_api.VkApi(token=acces_token)
        self.offset = 0
        
    def _bdate_toyear(self, bdate):
        user_year = bdate.split('.')[2]
        now = datetime.now().year
        return now - int(user_year)

    def get_profile_info(self, user_id: int):

        try:
            info, = self.vkapi.method('users.get',
                                      {'user_id': user_id,
                                       'fields': 'city,sex,relation,bdate'
                                       }
                                      )
        except ApiError as e:
            info = {}
            print(f'error = {e}')

        result = {'name': (info['first_name'] + ' ' + info['last_name']) if
                  'first_name' in info and 'last_name' in info else None,
                  'sex': info.get('sex'),
                  'city': info.get('city')['title'] if info.get('city') is not None else None,
                  'year': self._bdate_toyear(info.get('bdate'))
                  }
        return result
    
    def search_worksheet(self, params, offset):
        try:
            users = self.vkapi.method('users.search',
                                      {
                                          'count': 10,
                                          'offset': offset,
                                          'hometown': params['city'],
                                          'sex': 1 if params['sex'] == 2 else 2,
                                          'has_photo': True,
                                          'age_from': params['year'] - 3,
                                          'age_to': params['year'] + 3,
                                      }
                                      )
        except ApiError as e:
            users = []
            print(f'error = {e}')

        result = [{'name': item['first_name'] + item['last_name'],
                   'id': item['id']
                   } for item in users['items'] if item['is_closed'] is False
                  ]

        return result

    def get_city(self, city_name):
        # Получение отсутствующего города в профиле

        res = ""
        city_name = (city_name[:15]) if len(city_name) > 15 else city_name
        cities = self.vkapi.method("database.getCities",
                                 {'items': 0,
                                  'city_name': city_name,
                                  'count': 10,
                                  'offset': 0,
                                  'q': city_name,
                                  'need_all': True
                                  }
                                 )
        try:
            cities = cities['items']
        except KeyError as e:
            print(f'KeyError = {e}')
            cities = []
        for city in cities:
            if city_name.lower() == city['title'].lower():
                result = city['title']
        return result if result != "" else "Error"    
                        
    def get_photos(self, id):
        try:
            photos = self.vkapi.method('photos.get',
                                       {'owner_id': id,
                                        'album_id': 'profile',
                                        'extended': 1
                                        }
                                       )
        except ApiError as e:
            photos = {}
            print(f'error = {e}')

        result = [{'owner_id': item['owner_id'],
                   'id': item['id'],
                   'likes': item['likes']['count'],
                   'comments': item['comments']['count']
                   } for item in photos['items']
                  ]
        '''сортировка п лайкам и комментам'''
        
        result.sort(key=lambda x: x['likes']+x['comments']*10, reverse=True)

        return result[:3]
    
    
if __name__ == '__main__':
    user_id = " "
    tools = VkTools(acces_token)
    params = tools.get_profile_info(user_id)
    worksheets = tools.search_worksheet(params, 20)
    worksheet = worksheets.pop()
    photos = tools.get_photos(worksheet['id'])
    #pprint(worksheets)
    #pprint(tools.search_worksheet())
    pprint(photos)


