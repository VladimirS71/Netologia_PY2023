# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from backend import VkTools
from data_base import create_db, VK_Data_Base
# отправка сообщения



class BotInterface():
    vk_tools = False
    def __init__(self, comunity_token, acces_token):
        self.vk = vk_api.VkApi(token=comunity_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(acces_token)
        self.params = {}
        self.worksheets = []
        self.offset = 0
        self.data = VK_Data_Base()
        
       

    def message_send(self, user_id, message, attachment=None):
        self.vk.method('messages.send',
                       {'user_id': user_id,
                        'message': message,
                        'attachment': attachment,
                        'random_id': get_random_id()}
                       )
        
    def get_worksheet(self, user_id):
        #делаем запрос в бд
        #если вернулся фолс работаем с ней дальше
        if not self.data.viewed_id(id(['id']), user_id):
            # делаем запрос в бэк боту - он у себя уже обрабатывает и возвращает ссылку на фотки
            # получаем фото 
            return self.vk_tools.get_photos(user_id)
        return self.get_worksheet()
    
    def _get_profiles(self, users: list):
            """Функция генератор
            Запрашивает список анкет с указанными параметрами
            анкета сверяется с БД, если записи по id анкеты нет - 
            добавляем в БД анкету как просмотренную 
            :profiles: список id которые вернул запрос поиска
            :yield: словарь:
                'id': 123,
                'f': Полное имя анкеты"""
            while True:
                if users:
                    user = users.pop()
                    if not self.data.viewed_id(user_id=self.params['id'], worksheet_id=user['id']):
                        self.data.add_user(user_id=self.params['id'], worksheet_id=user['id'])
                        yield user
                else:
                    users = self.vk_tools.search_worksheet(params=self.params)
                    if not users:
                        yield None

# обработка событий / получение сообщений

    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    '''Логика для получения данных о пользователе'''
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.message_send(
                        event.user_id, f'Привет друг, {self.params["name"]}')
                elif event.text.lower() == 'поиск':
                    '''Логика для поиска анкет'''
                    self.message_send(
                        event.user_id, 'Начинаем поиск')
                    flag = True
                    # запускаем вечный цикл
                    while flag: 
                        # если список пуст запускаем новый
                        if not self.worksheets:
                            self.worksheets = self.vk_tools.search_worksheet(self.params, self.offset)
                            self.offset += 10
                        worksheet = self.worksheets.pop()
                        attach = self.get_worksheet(worksheet['id'])
                        # если анкета прошла здесь уже фотки 
                        if attach: 
                            break
                    self.message_send(
                                event.user_id,
                                f'имя: {worksheet["name"]} ссылка: vk.com/{worksheet["id"]}',attachment = attach
                            )
 
                elif event.text.lower() == 'пока':
                    self.message_send(
                        event.user_id, 'До новых встреч')
                else:
                    self.message_send(
                        event.user_id, 'Неизвестная команда')


if __name__ == '__main__':
    bot_interface = BotInterface(comunity_token, acces_token)
    #bot_interface.event_handler()
    eng = BotInterface(comunity_token, acces_token)
    attach = eng.get_worksheet(311363878)
    print(attach)
