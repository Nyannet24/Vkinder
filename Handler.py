# Работа с VK_API
import vk_api
# Работа с веб запросами
import requests # (для скачивания фото)
# Работа с операционной системой
import os # (Для проверки и создания папки Images)
# Работа с загрузкой файла в сообщении
from vk_api import VkUpload
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
    def CalculateAge(self, bdate):
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
    def GetRelation(self, relation):
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
    def GetUserInfo(self, user_id, Update):
        try:
            # Получаем полную информацию о ползователе
            user_info = self.user_vk.users.get(user_ids=user_id, fields='bdate,sex,city,relation')[0]
            # Получаем возраст
            age = self.CalculateAge(user_info['bdate'])
            # Получаем пол
            sex = self.GetSex(user_info['sex'])
            # Получаем город
            city = user_info.get('city', {})
            # Получаем семейное положение
            relation = self.GetRelation(user_info.get('relation'))
            # Если по семейному положению пользователь уже в 'оковах'
            if relation == 3 or relation == 4 or relation == 8:
                self.send_message_kb(user_id, "Ой! Кажись твое семейное положение не позволяет пользоваться ботом\
                                \nОбнови семейное положение и возвращайся обратно", self.KB.Create())
            else:
                self.send_message_kb(user_id, f"Я собрал о тебе некоторую информацию:\n\
                                    \nВозраст: {age}\
                                    \nПол: {sex}\
                                    \nГород: {city.get('title', 0)}\
                                    \nСемейное положение: {relation}\n\
                                    \nЕсли данные не актуальные, обнови профиль ВК и после профиль в боте", self.KB.Menu())
                # Проверка на регистрацию или обновление уже имеющейся информации (проверка для избежания дублирования кода)
                if Update:
                    self.db.UpdateUser([user_id, user_info['sex'], age, city.get('id', 0), relation])
                else:
                    self.db.CreateUser([user_id, user_info['sex'], age, city.get('id', 0), relation])
                
        except vk_api.exceptions.VkApiError as err:
            print(f"Ошибка при получении информации о пользователе: {err}")
            self.send_message_kb(user_id, "Произошли непредвиденные ошибки!\nПопробуй создать профиль чуть позже", self.KB.Create())
    
    # Метод для скачивания отсортированных фото (до 3)
    def DownloadsPhotos(self, photos):
        # Получаем текущую папку скрипта
        current_dir = os.getcwd()
        # Создаем новый путь с папкой Images
        folder_path = os.path.join(current_dir, "Images")
        # Проверяем существует ли указанная папка
        if not os.path.exists(folder_path):
            # Если не существует, создаем ее
            os.makedirs(folder_path)
        
        # Проходимся по всем полученным фоткам (отсортированным) и скачиваем их в указанную папку
        for i in range(len(photos)):
            p = requests.get(photos[i])
            out = open(os.getcwd() + f"/Images/{i}.jpg", "wb")
            out.write(p.content)
            out.close()
    
    # Метод отправки сообщения с картинками (в виде файлов), текстом и клавиатурой
    def SendMsgWithPhotoAndKb(self, user_id, folder_path, message, keyboard):
        # Открываем загрузку фото в сообщение
        upload = VkUpload(self.vk_session)
        # Создаем дополнительные переменные
        photos = []
        attachments = ""
        # Получаем список файлов из папки
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        # Загружаем и добавляем каждую картинку в список photos
        for file in files:
            photo_path = os.path.join(folder_path, file)
            photo = upload.photo_messages(photo_path)
            photos.append(photo[0])
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
    def GetSortedPhotos(self, user_id):
        # Исходные параметры для запроса
        params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1
        }
        try:
            # Запрашиваем фото
            photos_response = self.user_vk.photos.get(**params)
            # Сортируем фото по количеству лайков
            sorted_photos = sorted(photos_response['items'], key=lambda x: x['likes']['count'], reverse=True)
            # Обрезаем до 3 элементов
            top_photos = sorted_photos[:3]
            # Создаем дополнительную переменную для формирования списка ссылок
            links = []
            # Проходимся по оставшимся фото и скачиваем их
            for i, photo in enumerate(top_photos, start=1):
                links.append(photo['sizes'][-1]['url'])
            # Скачиваем полученные фото по их ссылке
            self.DownloadsPhotos(links)
            return links
        except vk_api.VkApiError as e:
            print(f"Error: {e}")
            return None
    
    # Метод для поиска подходящего пользователя
    def SearchUsers(self, user_id):
        # Получаем характеристики профиля для параметров поиска
        me = self.db.GetUser(user_id)
        sex = me[0]
        age = me[1]
        city = me[2]
        try:
            # Создаем переменную со смещением (это нужно для обхода ограничения поиска)
            Offset = self.db.GetUserOffset(user_id)
            # Задаем параметры для поиска (с лимитом 1 человек)
            params = {
                'offset': Offset, # Смещение поиска (обход максимальной выдачи из 1000 пользователей)
                'count': 1,  # Количество результатов поиска
                'fields': 'sex,city,relation',  # Поля, которые нужно получить для каждого пользователя
                'age_from': age - 3,  # Минимальный возраст (минус 3 от текущего нашего)
                'age_to': age + 3,  # Максимальный возраст (плюс 3 от текущего нашего)
                'sex': 1 if sex == 2 else 1,  # Пол (1 - женский, 2 - мужской)
                'city': city,  # Идентификатор города
                'has_photo': 1 # Есть ли фото
            }
            # Получаем подходящего пользователя
            User = self.user_vk.users.search(**params)
            # Получаем ID пользователя
            PairID = User['items'][0]['id']
            # Если смещение оказалось больше количества подходящих профилей (всего), то обновляем смещение
            if Offset > int(User['count']):
                self.send_message(user_id, "Кажись ты посмотрел всевозможные анкеты по заданным критериям\
                            \nОчищаю базу данных от оцененных анкет")
                # Удаляем оцененные анкеты из базы данных
                self.db.DeleteMatchHistory()
                # Устанавливаем новое найденное значение подходящих анкет
                self.db.SetUserMax(user_id, User['count'])
                # Обнуляем смещение
                self.db.GetUserOffset(user_id, 0)
                # Запускаем новый поиск
                self.SearchUsers(user_id, sex, age, city)
            else:    
                # Увеличиваем смещение на 1
                self.db.AddUserOffset(user_id)
                # Если у пользователя профиль открыт и его еще не оценили
                if not User['items'][0].get('is_closed', False) and self.db.GetCountMatchFromPair(PairID):
                    # Временно сохраняем ID пользователя
                    self.db.SetUserItems(user_id, PairID)
                    # Получаем и сортируем фото пользователя
                    self.GetSortedPhotos(PairID)
                    # Получаем имя и фамилию пользователя
                    Name = f"{User['items'][0]['first_name']} {User['items'][0]['last_name']}"
                    # Получаем семейное положение пользователя
                    if 'relation' in User['items'][0]:
                        Relation = User['items'][0]['relation']
                    else:
                        Relation = 0
                    # Формируем сообщение в виде анкеты для оценки
                    self.SendMsgWithPhotoAndKb(user_id, os.getcwd() + f"/Images/", f"Имя: {Name}\
                                            \nСП: {self.GetRelation(Relation)}", self.KB.SearchPair())
                    # После успешной отправки анкеты удаляем фото пользователя с компьютера
                    files = os.listdir(os.getcwd() + f"/Images/")
                    # (Удаляются все файлы из папки Images)
                    for file in files:
                        file_path = os.path.join(os.getcwd() + f"/Images/", file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                else:
                    # Иначе перезапускаем поиск с новым смещением
                    self.SearchUsers(user_id, sex, age, city)
    
        except vk_api.exceptions.VkApiError as err:
            print(f"Ошибка при выполнении поиска пользователей: {err}")
            self.send_message_kb(user_id, f"Не удалось отобразить профиль\nПродолжаем поиск пар?", self.KB.SearchPairContinue())