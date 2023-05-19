#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Подключаемые библиотеки
# Работа с VK API
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
# Работа с базой данных
from SQL import SQL
# Работа с клавиатурой в сообщениях
from Keyboards import Keyboards
# Работа с датами (для БД)
from datetime import datetime



# Переменные 
db = SQL() # Для взаимодействия с классом базы данных
KB = Keyboards() # Для взаимодействия с классом клавиатуры

# Инициализация бота
token = 'vk1.a.VDyct2tV-1-tEUP6ukYLwW0cLntPHj3RJp4mLpSgFrOm7MBmhTe26Hg3CADNUn9VgU2YMUf883BIeXYgj4245TucF9LYBbVDzPLsIYe6X2yfOm2RG55LQDfECjlBu5HiiS_4D42VdgNZ-eFsO5Ff0UhGlg9vuvFosykG1_uCP4FnVPQZwRmrDyIIebA5y-ynoXywt9lihThMLlEsCh55hA'
group_id = 'vk1.a.NKGNxBoXeTQBx19u0P1qKhUVbn2-wByN2UmNUuyqOvVWo2kImUrxKKketkDObphcD3zRW-pQaOx7GTjApjVG9BK6nyVtmmuOeoTgb9hTEzVVwHVet2disAoQS48H4j7QBDT4YN-vy-ytRjRcC2o1NvdVuhFsFEjECRZYAcbSGQi0rJjJPj1f5pi1RyhmDay-uzsRy7RqcddoIlq2Vm3gsQ'
vk_session = vk_api.VkApi(token=token)
longpoll = VkBotLongPoll(vk_session, group_id)
vk = vk_session.get_api()



# Функция для отправки сообщения с клавиатурой
def send_message_kb(peer_id, message, keyboard):
    vk.messages.send(
                random_id=vk_api.utils.get_random_id(),
                peer_id=peer_id,
                message=message,
                keyboard=keyboard.get_keyboard()
            )



# Функция отправки сообщения
def send_message(peer_id, message):
    vk.messages.send(
                random_id=vk_api.utils.get_random_id(),
                peer_id=peer_id,
                message=message
            )



# Функция регистрация пользователя
def CreateUser(message, peer_id):
    # Пытаемся получить геопозицию
    try:
        # Широта пользователя
        Latitude = message['geo']['coordinates']['latitude'] 
        # Долгота пользователя
        Longitude = message['geo']['coordinates']['longitude'] 
        # Город пользователя
        City = message['geo']['place']['city'] 
        # Пытаемся получить данные из профиля 
        try:
            # Получаем информацию о пользователе
            Responce = vk.users.get(user_ids=peer_id, fields='sex, bdate')
            # Получаем пол пользователя (1 - Ж, 2 - М)
            Sex = Responce[0]['sex'] 
            # Получаем возраст пользователя
            BDay = int(datetime.now().year) - int(Responce[0]['bdate'].split('.')[-1]) 
            # Создаем пользователя в базе данных
            db.CreateUser([peer_id, Sex, BDay, Latitude, Longitude, City]) 
            # Отправляем сообщение об успешной регистрации
            send_message_kb(peer_id, 'Отлично! Регистрация успешно пройдена\U0001F603', KB.Menu())

        except Exception as err:
            print(f"Возраст недоступен. Ошибка {err}")
            # Отправляем сообщение об ошибке при регистрации
            send_message(peer_id, 'Ой, кажись мне не удалось обработать твои данные с профиля!\U0001F633\
                            \nОткрой информацию к своей дате рождения')

    except Exception as err:
        print(f"Геолокация недоступна. Ошибка {err}")
        # Отправляем сообщение об ошибке при регистрации
        send_message(peer_id, 'Ой, кажись мне не удалось обработать твою геолокацию!\U0001F633\
                        \nПопробуй еще раз чуть позже')



# Функция обновления информации о пользователе
def UpdateUser(message, peer_id):
    # Пытаемся получить геопозицию
    try:
        # Широта пользователя
        Latitude = message['geo']['coordinates']['latitude'] 
        # Долгота пользователя
        Longitude = message['geo']['coordinates']['longitude'] 
        # Город пользователя
        City = message['geo']['place']['city'] 
        # Пытаемся получить данные из профиля 
        try:
            # Получаем информацию о пользователе
            Responce = vk.users.get(user_ids=peer_id, fields='sex, bdate')
            # Получаем пол пользователя (1 - Ж, 2 - М)
            Sex = Responce[0]['sex'] 
            # Получаем возраст пользователя
            BDay = int(datetime.now().year) - int(Responce[0]['bdate'].split('.')[-1]) 
            # Обновляем пользователя в базе данных
            db.UpdateUser(peer_id, Sex, BDay, Latitude, Longitude, City) 
            # Отправляем сообщение об успешном обновлении анкеты
            send_message_kb(peer_id, 'Отлично! Данные анкеты обновлены\U0001F603', 
                            KB.Menu() if db.GetUserActive(peer_id) == 1 else KB.MenuSleep())

        except Exception as err:
            print(f"Возраст недоступен. Ошибка {err}")
            # Отправляем сообщение об ошибке при обновлении анкеты
            send_message(peer_id, 'Ой, кажись мне не удалось обработать твои данные с профиля!\U0001F633\
                            \nОткрой информацию к своей дате рождения', 
                            KB.Menu() if db.GetUserActive(peer_id) == 1 else KB.MenuSleep())

    except Exception as err:
        print(f"Геолокация недоступна. Ошибка {err}")
        # Отправляем сообщение об ошибке при обновлении анкеты
        send_message(peer_id, 'Ой, кажись мне не удалось обработать твою геолокацию!\U0001F633\
                        \nПопробуй еще раз чуть позже', 
                        KB.Menu() if db.GetUserActive(peer_id) == 1 else KB.MenuSleep())



# Функция поиска анкет подходящих по критериям
def SearchMatch(peer_id):
    UserInfo = db.GetUser(peer_id)
    Result = db.SearchPair(peer_id, UserInfo[1], UserInfo[2])
    # Проверка наличия анкет в переменной Result после поиска
    if not Result is None:
        # Отображаем найденную анкету
        ViewUser(Result[0], peer_id) 
    else:
        send_message_kb(peer_id, 'Ой! Кажись ты посмотрел все доступные анкеты\nВозвращайся чуть позже!', KB.Menu())



# Функция отображения анкеты пользоватей
def ViewUser(PairID, peer_id):
    try:
        # Временно сохраняем выбранную пару для оценки
        db.SetUserPair(peer_id, PairID) 
        # Получаем информацию о паре
        Pair = vk.users.get(user_ids=PairID, fields='status,photo_max_orig') 
        # Получаем имя пары
        PairName = Pair[0]['first_name']  
        # Получаем статус пары
        Status = Pair[0]['status']  
        # Получаем ссылку на аватарку пары
        Photo = Pair[0]['photo_max_orig']
        # Получаем дистанцию в км между нами и парой
        Distance = int(db.SearchDistance(peer_id, PairID))
        # Получаем возраст пары
        PairYear = db.GetUserAge(PairID)
        # Формируем текст для сообщения
        Text = f"{PairName}, {Distance} км, {PairYear}\n\n{Status}" # Текст к картинам (Имя, расстояние, статус в профиле пары)
        # Отправляем сообщение с текстом и картинками
        vk.messages.send(user_id=peer_id, attachment=Photo, message=Text,
                            random_id=vk_api.utils.get_random_id(),
                            keyboard=KB.SearchPair().get_keyboard())
    except Exception as err:
        print(f"Не удалось отобразить анкеты при поиске. Ошибка {err}")
        SearchMatch(peer_id)



# Функция отображения анкеты при уведомлении о Мэтче
def SendPair(PairID, peer_id):
    try:
        # Получаем информацию о пользователе
        Pair = vk.users.get(user_ids=peer_id, fields='status,photo_max_orig')
        # Получаем имя пользователя
        PairName = Pair[0]['first_name']  
        # Получаем статус пары
        Status = Pair[0]['status']  
        # Получаем ссылку на аватарку пары
        Photo = Pair[0]['photo_max_orig']
        # Получаем дистанцию в км между нами и парой
        Distance = int(db.SearchDistance(peer_id, PairID))
        # Получаем возраст пары
        PairYear = db.GetUserAge(peer_id)
        # Формируем текст для сообщения
        Text = f"Тебя лайкнули - {PairName}, {Distance} км, {PairYear}\n\n{Status}\n\
                \nЕго ссылка https://vk.com/id{peer_id}\n\nУдачного общения!"
        # Отправляем сообщение с текстом и картинками
        vk.messages.send(user_id=PairID, attachment=Photo, message=Text,
                        random_id=vk_api.utils.get_random_id(),
                        keyboard=KB.SearchPair().get_keyboard())
    except Exception as err:
        # Отправляем сообщение с ссылкой на лайкнувшего без фото и прочей информации (при проблемах получения информации)
        send_message_kb(PairID, f'Тебя лайкнули!\nНо мне не удалось прикрепить всю информацию\
                                \n Лайк от https://vk.com/id{peer_id}', KB.Menu())
        print(f"Ошибка при оправке мэтча паре. Ошибка {err}")



# Функция запуска поллинга бота
def StartBot():
    # Обработка событий
    for event in longpoll.listen():
        # Если это событие в сообщениях бота (Если доступ только к сообщениям, то можно удалить проверку)
        if event.type == VkBotEventType.MESSAGE_NEW:
            # Получаем информацию о сообщении
            message = event.obj.message
            # Получаем информацию о пользователе
            Response = vk.users.get(user_ids=message['from_id'])
            # Получаем айди пользователя
            peer_id = message['peer_id']
            print(peer_id)
            # Проверяем профиль пользователя на приватность
            if not Response[0]['is_closed']:
                # Проверяем есть ли анкета пользователя в боте
                if db.CheckUser(peer_id):
                    # Далее идет команды взаимодействия с ботом
                    match message['text'].lower():
                        case 'поиск':
                            # Уведомляем пользователя о поиске анкет
                            send_message(peer_id, 'Начинаю поиск анкет')
                            # Запускаем поиск анкет
                            SearchMatch(peer_id)

                        case 'обновить профиль':
                            Active = db.GetUserActive(peer_id)
                            send_message_kb(peer_id, 'Пришли свою геолокацию', KB.Menu() if Active == 1 else KB.MenuSleep())

                        case 'уйти в сон':
                            # Меняем активность анкеты пользователя
                            db.SetUserActive(peer_id, 0)
                            send_message_kb(peer_id, 'Твой профиль ушел в сон!\nЭто значит, что ты пока не будешь отображаться в поиске', KB.MenuSleep())

                        case 'проснуться':
                            # Меняем активность анкеты пользователя
                            db.SetUserActive(peer_id, 1)
                            send_message_kb(peer_id, 'Доброе утро! Твой профиль проснулся и теперь отображается в поиске', KB.Menu())

                        case 'лайк':
                            # Получаем айди владельца анкеты, которую лайкнули
                            Pair = db.GetUserPair(peer_id)
                            # Добавляем результат оценки анкеты в таблицу
                            db.SetMatchHistory(peer_id, Pair, 1)
                            # Уведомляем пару о мэтче
                            SendPair(Pair, peer_id)
                            # Продолжаем поиск анкет
                            SearchMatch(peer_id)

                        case 'дизлайк':
                            # Добавляем результат оценки анкеты в таблицу
                            db.SetMatchHistory(peer_id, db.GetUserPair(peer_id), 0)
                            SearchMatch(peer_id)

                        case 'уйти в меню':
                            send_message_kb(peer_id, 'Ты вернулся в меню', KB.Menu())

                        case _:
                            if 'geo' in message:
                                UpdateUser(message, peer_id)
                            else:
                                # Возвращаем ответ на нештатную команду с выбором меню (команда может поступить как от активного, так и неактивного пользователя)
                                send_message_kb(peer_id, 'Не совсем понял твою команду', KB.Menu() if db.GetUserActive(peer_id) == 1 else KB.MenuSleep())
                else:
                    # Регистрация пользователя
                    # Если пользователь прислал геопозицию
                    if 'geo' in message:
                        CreateUser(message, peer_id)
                    else:
                        send_message(peer_id, 'Чтобы начать пользоваться VKinder, нужно отправить свою геолокацию')
            else:
                # Уведомление о приватном профиле
                # Если анкета профиля в боте есть, закрываем ее 
                if db.CheckUser(peer_id):
                    db.SetUserActive(peer_id, 0)

                send_message(peer_id, 'Твой профиль закрыт настройками приватности\
                                    \nОткрой профиль, чтобы продолжить пользоваться VKinder\U00002764\U0000FE0F')



# Вход программы
if __name__ == "__main__":
    # Ставим базу данных
    db.SetDB()
    # Запускаем поллинг бота
    StartBot()