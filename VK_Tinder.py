#!/usr/bin/env python3
# -*- coding: utf-8 -*-


####### Подключаемые библиотеки

# Работа с VK API
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
# Работа с базой данных
from SQL import SQL
# Работа с клавиатурой в сообщениях
from Keyboards import Keyboards
# Работа с клавиатурой в сообщениях
from Handler import Handler

# Инициализация бота
token = 'Токен_Группы'
group_id = 'Айди_Группы'
vk_session = vk_api.VkApi(token=token)
longpoll = VkBotLongPoll(vk_session, group_id)
vk = vk_session.get_api()

# https://oauth.vk.com/authorize?client_id=ТОКЕН_Standalone_Приложения&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=offline,photos,wall,groups,docs,status,notes,pages,stats,notifications,ads,offline,docs,pages,stats,notifications,email,market&response_type=token&v=5.131
# Заменить ТОКЕН_Standalone_Приложения на Ваш токен для получения пользовательского токена
# (в данной ссылке задан доступ ко всему аккаунту)
user_token = 'Токен_Пользователя'
user_vk_session = vk_api.VkApi(token=user_token)
user_vk = user_vk_session.get_api()

# Переменные 
db = SQL() # Для взаимодействия с классом базы данных
KB = Keyboards() # Для взаимодействия с классом клавиатуры
h = Handler(vk, user_vk, vk_session) # Для взаимодействия с классом обработчика событий



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
            # Проверяем профиль пользователя на приватность
            if not Response[0]['is_closed']:
                # Если пользователь есть в базе данных
                if db.CheckUser(peer_id):

                    match message['text'].lower():

                        case "обновить профиль":
                            # Обновляем профиль пользователя
                            h.GetUserInfo(peer_id, True)

                        case "поиск":
                            # Поиск подходящих пользователей по нашим критериям
                            h.SearchUsers(peer_id)

                        case "да":
                            # Подтверждения поиска подходящих пользователей после лайка
                            h.SearchUsers(peer_id)

                        case "уйти в меню":
                            # Выход из поиска в меню
                            h.send_message_kb(peer_id, "Поиск остановлен, ты в меню", KB.Menu())

                        case "лайк":
                            # Получаем ID пользователя
                            PairID = db.GetUserItems(peer_id)
                            # Сохраняем результат оценки в базу данных
                            db.SetMatchHistory(PairID, 1)
                            h.send_message_kb(peer_id, f"Приятного общения!\
                            \nСсылка: vk.com/id{PairID}\n\
                            \nПродолжаем поиск пар?", KB.SearchPairContinue())

                        case "дизлайк":
                            # Получаем ID пользователя
                            PairID = db.GetUserItems(peer_id)
                            # Сохраняем результат оценки в базу данных
                            db.SetMatchHistory(PairID, 0)
                            # Продолжаем поиск подходящих пользователей
                            h.SearchUsers(peer_id)

                        case _:
                            h.send_message_kb(peer_id, "Не совсем понял твою команду", KB.Menu())

                else:

                    match message['text'].lower():

                        case "создать профиль":
                            # Регистрируем профиль пользователя
                            h.GetUserInfo(peer_id, False)

                        case _:
                            h.send_message_kb(peer_id, "Привет! Мне нужно получить твои данные, чтобы начать подбирать пару", KB.Create())

            else:
                h.send_message(peer_id, 'Твой профиль закрыт настройками приватности\
                                    \nОткрой профиль, чтобы продолжить пользоваться VKinder\U00002764\U0000FE0F')



# Вход программы
if __name__ == "__main__":
    # Ставим базу данных
    db.SetDB()
    # Запускаем поллинг бота
    StartBot()
