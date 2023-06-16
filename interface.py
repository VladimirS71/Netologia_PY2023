# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from backend import VkTools
from data_store import VK_Data_Base
# отправка сообщения



class BotInterface():
    vk_tools = False

    def __init__(self, comunity_token, acces_token):
        self.vk = vk_api.VkApi(token=comunity_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(acces_token)
        self.params = None
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
    
# обработка событий / получение сообщений

    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    '''Логика для получения данных о пользователе'''
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.message_send(
                        event.user_id, f'Привет друг, {self.params["name"]}')
                     # обработка данных, которых недостаточно
                    self.keys = self.params.keys()
                    for i in self.keys:
                        if self.params[i] is None:
                            if self.params['city'] is None:
                                self.message_send(event.user_id, f'Введите город: ')
                                for event_listen in self.longpoll.listen():
                                    if event_listen.type == VkEventType.MESSAGE_NEW and event_listen.to_me:
                                        res = self.vk_tools.get_city(event_listen.text.lower())
                                        if res == "Error":
                                            self.message_send(event_listen.user_id,
                                                            f'Вы ввели неизвестный город. 
                                                                Введите город: ')
                                        else:
                                            self.params['city'] = event_listen.text.lower()
                                            break

                            elif self.params['year'] is None:
                                self.message_send(event.user_id, f'Введите дату рождения (дд.мм.гггг): ')
                                for event_listen in self.longpoll.listen():
                                    if event_listen.type == VkEventType.MESSAGE_NEW and event_listen.to_me:
                                        if event_listen.text.lower().isdigit() and len(event_listen.text.lower()) == 4:
                                            self.params['year'] = int(datetime.now().today().year) - int(event_listen.text.lower())
                                            break
                                        else:
                                            self.message_send(event.user_id, f'Введите дату рождения (дд.мм.гггг): ')

                            self.message_send(event.user_id, 'Вы авторизовались!')
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
                        photo_string = ''
                        for photo in attach:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                        # если анкета прошла здесь уже фото
                        if attach:
                            if not self.data.viewed_id(user_id=event.user_id, worksheet_id=worksheet['id']):
                                self.data.add_user(user_id=event.user_id, worksheet_id=worksheet['id']) 
                            break
                    self.message_send(
                                event.user_id,
                                f'имя: {worksheet["name"]} ссылка: vk.com/{worksheet["id"]}', attachment = photo_string
                            ) 
                
                elif event.text.lower() == 'в список избранных':
                    self.data.update_user(user_id = event.user_id, worksheet_id = worksheet["id"])   
                    self.message_send(
                        event.user_id, f'Анкета: {worksheet["name"]} добавлена в избранное')
                
                elif event.text.lower() == 'избранное':
                    favor = self.data.viewed_favorite(user_id = event.user_id)
                    self.message_send(event.user_id, f'Найдено анкет: {len(favor)}')

                elif event.text.lower() == 'удалить':
                    self.data.update_user(user_id = event.user_id, worksheet_id = worksheet["id"], favourites= False)   
                    self.message_send(
                        event.user_id, f'Анкета: vk.com/id{worksheet["id"]} удалена из избранного')

                elif event.text.lower() == 'пока':
                    self.message_send(
                        event.user_id, 'До новых встреч')
                else:
                    self.message_send(
                        event.user_id, 'Неизвестная команда')


if __name__ == '__main__':
    bot_interface = BotInterface(comunity_token, acces_token)
    bot_interface.event_handler()
    eng = BotInterface(comunity_token, acces_token)
    attach = eng.get_worksheet()
    photo_string = ''
    for photo in attach:
        photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
    print(attach)
