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
# Работа с функционалом бота
from Handler import Handler

# Инициализация бота
token = 'Токен_Группы'
group_id = 'Айди_Группы_'
vk_session = vk_api.VkApi(token=token)
longpoll = VkBotLongPoll(vk_session, group_id)
vk = vk_session.get_api()

# https://oautHlr.vk.com/authorize?client_id=ТОКЕН_Standalone_Приложения&display=page&redirect_uri=https://oautHlr.vk.com/blank.html&scope=offline,photos,wall,groups,docs,status,notes,pages,stats,notifications,ads,offline,docs,pages,stats,notifications,email,market&response_type=token&v=5.131
# Заменить ТОКЕН_Standalone_Приложения на Ваш токен для получения пользовательского токена
# (в данной ссылке задан доступ ко всему аккаунту)
user_token = 'Токен_Пользователя'
user_vk_session = vk_api.VkApi(token=user_token)
user_vk = user_vk_session.get_api()

# Переменные 
db = SQL() # Для взаимодействия с классом базы данных
KB = Keyboards() # Для взаимодействия с классом клавиатуры
Hlr = Handler(vk, user_vk, vk_session) # Для взаимодействия с классом обработчика событий



# Функция запуска поллинга бота
def start_bot():
    # Обработка событий
    for event in longpoll.listen():
        # Если это событие в сообщениях бота (Если доступ только к сообщениям, то можно удалить проверку)
        if event.type == VkBotEventType.MESSAGE_NEW:
            # Получаем информацию о сообщении
            message = event.obj.message
            # Получаем информацию о пользователе
            response = vk.users.get(user_ids=message['from_id'])
            # Получаем айди пользователя
            peer_id = message['peer_id']
            # Проверяем профиль пользователя на приватность
            if not response[0]['is_closed']:
                # Если пользователь есть в базе данных
                if db.check_user(peer_id):

                    match message['text'].lower():

                        case "обновить профиль":
                            # Обновляем профиль пользователя
                            Hlr.get_user_info(peer_id, True)

                        case "поиск":
                            # Поиск подходящих пользователей по нашим критериям
                            Hlr.search_users(peer_id)

                        case "да":
                            # Подтверждения поиска подходящих пользователей после лайка
                            Hlr.search_users(peer_id)

                        case "уйти в меню":
                            # Выход из поиска в меню
                            Hlr.send_message_kb(peer_id, "Поиск остановлен, ты в меню", KB.menu())

                        case "лайк":
                            # Получаем ID пользователя
                            pair_id = db.get_user_items(peer_id)
                            # Сохраняем результат оценки в базу данных
                            db.set_match_history(pair_id, 1)
                            # Удаляем пользователя из "партии"
                            db.delete_found(pair_id)
                            Hlr.send_message_kb(peer_id, f"Приятного общения!\
                            \nСсылка: vk.com/id{pair_id}\n\
                            \nПродолжаем поиск пар?", KB.search_pair_continue())

                        case "дизлайк":
                            # Получаем ID пользователя
                            pair_id = db.get_user_items(peer_id)
                            # Сохраняем результат оценки в базу данных
                            db.set_match_history(pair_id, 0)
                            # Удаляем пользователя из "партии"
                            db.delete_found(pair_id)
                            # Продолжаем поиск подходящих пользователей
                            Hlr.search_users(peer_id)

                        case _:
                            Hlr.send_message_kb(peer_id, "Не совсем понял твою команду", KB.menu())

                else:

                    match message['text'].lower():

                        case "создать профиль":
                            # Регистрируем профиль пользователя
                            Hlr.get_user_info(peer_id, False)

                        case _:
                            Hlr.send_message_kb(peer_id, "Привет! Мне нужно получить твои данные, чтобы начать подбирать пару", KB.create())

            else:
                Hlr.send_message(peer_id, 'Твой профиль закрыт настройками приватности\
                                    \nОткрой профиль, чтобы продолжить пользоваться VKinder\U00002764\U0000FE0F')



# Вход программы
if __name__ == "__main__":
    # Ставим базу данных
    db.set_db()
    # Запускаем поллинг бота
    start_bot()