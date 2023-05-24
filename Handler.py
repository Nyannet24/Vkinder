# Работа с VK_API
import vk_api
# Работа со временем
from datetime import datetime
# Работа с базой данных
from SQL import SQL
# Работа с клавиатурой
from Keyboards import Keyboards


class Handler():

    # Конструктор класса Handler
    def __init__(self, vk, user_vk, vk_session):
        self.vk = vk # Взаимодействие от лица бота
        self.user_vk = user_vk # Взаимодействие от лица пользователя
        self.vk_session = vk_session # Взаимодействие с сессией бота
        self.db = SQL() # Для взаимодействия с классом базы данных
        self.KB = Keyboards() # Для взаимодействия с классом клавиатуры

    # Метод для отправки сообщения с клавиатурой
    def send_message_kb(self, peer_id, message, keyboard):
        self.vk.messages.send(
                    random_id=vk_api.utils.get_random_id(),
                    peer_id=peer_id,
                    message=message,
                    keyboard=keyboard.get_keyboard()
                )
    
    # Метод отправки сообщения
    def send_message(self, peer_id, message):
        self.vk.messages.send(
                    random_id=vk_api.utils.get_random_id(),
                    peer_id=peer_id,
                    message=message
                )
    
    # Метод для расчета возраста пользователя по дате рождения
    def calculate_age(self, bdate):
        # Если даты нет
        if not bdate:
            return 'Не указан'
        # Разделяем дату
        birth_date = bdate.split('.')
        # Дополнительная проверка полученной даты
        if len(birth_date) == 3:
            # Преобразование даты в возраст в годах
            birth_year = int(birth_date[2])
            current_year = datetime.now().year
            age = current_year - birth_year
            return age
        else:
            return 'Не указан'
    
    # Метод для получения пола пользователя
    def GetSex(self, sex):
        # Пол пользователя
        if sex == 1:
            return 'Женский'
        elif sex == 2:
            return 'Мужской'
        else:
            return 'Не указан'

    # Метод для получения семейного положения пользователя
    def get_relation(self, relation):
        relation_dict = {
            1: 'Не женат/Не замужем',
            2: 'Есть друг/Подруга',
            3: 'Помолвлен/Помолвлена',
            4: 'Женат/Замужем',
            5: 'Всё сложно',
            6: 'В активном поиске',
            7: 'Влюблён/Влюблена',
            8: 'В гражданском браке'
        }
        return relation_dict.get(relation, 'Не указано')
    
    # Метод для получения полной информации о пользователе (При регистрации или обновлении информации)
    def get_user_info(self, user_id, Update):
        # Получаем полную информацию о ползователе
        user_info = self.user_vk.users.get(user_ids=user_id, fields='bdate,sex,city,relation')[0]
        # Получаем возраст
        age = self.calculate_age(user_info['bdate'])
        # Получаем пол
        sex = self.GetSex(user_info['sex'])
        # Получаем город
        city = user_info.get('city', {})
        # Получаем семейное положение
        relation = self.get_relation(user_info.get('relation'))
        # Если по семейному положению пользователь уже в 'оковах'
        if relation == 3 or relation == 4 or relation == 8:
            self.send_message_kb(user_id, "Ой! Кажись твое семейное положение не позволяет пользоваться ботом\
                            \nОбнови семейное положение и возвращайся обратно", self.KB.create())
        else:
            self.send_message_kb(user_id, f"Я собрал о тебе некоторую информацию:\n\
                                \nВозраст: {age}\
                                \nПол: {sex}\
                                \nГород: {city.get('title', 0)}\
                                \nСемейное положение: {relation}\n\
                                \nЕсли данные не актуальные, обнови профиль ВК и после профиль в боте", self.KB.menu())
            # Проверка на регистрацию или обновление уже имеющейся информации (проверка для избежания дублирования кода)
            if Update:
                self.db.update_user([user_id, user_info['sex'], age, city.get('id', 0), relation])
            else:
                self.db.create_user([user_id, user_info['sex'], age, city.get('id', 0), relation])
       
    # Метод отправки сообщения с картинками (в виде файлов), текстом и клавиатурой
    def send_with_photo_kb(self, user_id, message, keyboard, photos):
        # Создаем дополнительные переменные
        attachments = ""
        # Формируем attachments из списка фотографий
        for photo in photos:
            attachments += f"photo{photo['owner_id']}_{photo['id']},"
        # Отправляем сообщение с картинками, текстом и клавиатурой
        self.vk.messages.send(
            user_id=user_id,
            message=message,
            attachment=attachments,
            keyboard=keyboard.get_keyboard(),
            random_id=vk_api.utils.get_random_id()
        )
        
    # Метод получения всех фото пользователя и сортировки по лайкам (возвращется до 3 фото)
    def get_sorted_photos(self, user_id):
        # Исходные параметры для запроса
        params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1
        }
        # Запрашиваем фото
        photos_response = self.user_vk.photos.get(**params)
        # Сортируем фото по количеству лайков
        sorted_photos = sorted(photos_response['items'], key=lambda x: x['likes']['count'], reverse=True)
        # Обрезаем до 3 элементов
        top_photos = sorted_photos[:3]
        # Возвращаем ссылки на фото
        return top_photos

    # Метод для получения следующей партии подходящих анкет в размере 50 человек
    def set_new_founds(self, user_id):
        # Получаем информацию о своем профиле
        me = self.db.get_user(user_id)
        # Пол
        sex = me[0]
        # Возраст
        age = me[1]
        # Город
        city = me[2]
        # Создаем переменную со смещением (это нужно для обхода ограничения поиска)
        offset = self.db.get_user_offset(user_id)
        # Задаем параметры для поиска (с лимитом 50 человек)
        params = {
            'offset': offset, # Смещение поиска (обход максимальной выдачи из 1000 пользователей)
            'count': 50,  # Количество результатов поиска
            'fields': 'sex,city,relation',  # Поля, которые нужно получить для каждого пользователя
            'age_from': age - 3,  # Минимальный возраст (минус 3 от текущего нашего)
            'age_to': age + 3,  # Максимальный возраст (плюс 3 от текущего нашего)
            'sex': 1 if sex == 2 else 1,  # Пол (1 - женский, 2 - мужской)
            'city': city,  # Идентификатор города
            'has_photo': 1 # Есть ли фото
        }
        # Получаем подходящих пользователей
        users = self.user_vk.users.search(**params)
        # Увеличиваем смещение на 50
        self.db.add_user_offset(user_id)
        # Если смещение больше количества найденных людей
        if offset > int(users['count']):
            self.send_message(user_id, "Кажись ты посмотрел всевозможные анкеты по заданным критериям\
                        \nОчищаю базу данных от оцененных анкет")
            # Удаляем оцененные анкеты из базы данных
            self.db.delete_match_history()
            # Устанавливаем новое найденное значение подходящих анкет
            self.db.set_user_max(user_id, users['count'])
            # Обнуляем смещение
            self.db.set_user_offset(user_id, 0)
            # Получаем анкету на оценку
            self.search_users(user_id)
        else:
            # Проходимся по каждой анкете пользователя
            for user in users['items']:
                # Получаем его айди
                pair_id = user['id']
                # Если эта анкета еще не была оценена
                if self.db.get_count_match_from_pair(pair_id):
                    # Получаем приватность профиля
                    profile = user.get('is_closed', False)
                    # Получаем Имя и Фамилию пользователя
                    name = f"{user['first_name']} {user['last_name']}"
                    # Получаем семейное положение пользователя
                    relation = user.get('relation', 0)
                    # Добавляем пользователя в базу данных
                    self.db.create_found([pair_id, name, relation, profile])
            # Проверяем есть в новой партии пользователей неоцененные анкеты
            if self.db.get_count_found():
                # Если их 0, то получаем следующую партию пользователей
                self.set_new_founds(user_id)
            else:
                # Получаем анкету на оценку
                self.search_users(user_id)

    # Метод для поиска подходящего пользователя
    def search_users(self, user_id):
        if self.db.get_count_found():
            # Получаем характеристики профиля для параметров поиска
            self.set_new_founds(user_id)
        else:    
            # Получаем информацию пользователя текущей анкеты
            user = self.db.get_found()
            # Если у пользователя профиль открыт
            if user[3]:
                # Временно сохраняем ID пользователя
                self.db.set_user_items(user_id, user[0])
                # Получаем и сортируем фото пользователя
                links = self.get_sorted_photos(user[0])
                # Формируем сообщение в виде анкеты для оценки
                self.send_with_photo_kb(user_id, f"Имя: {user[1]}\nСП: {self.get_relation(user[2])}", self.KB.search_pair(), links)