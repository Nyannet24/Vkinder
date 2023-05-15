import vk_api

# авторизация ВК бота
vk_session = vk_api.VkApi(token='vk1.a.VDyct2tV-1-tEUP6ukYLwW0cLntPHj3RJp4mLpSgFrOm7MBmhTe26Hg3CADNUn9VgU2YMUf883BIeXYgj4245TucF9LYBbVDzPLsIYe6X2yfOm2RG55LQDfECjlBu5HiiS_4D42VdgNZ-eFsO5Ff0UhGlg9vuvFosykG1_uCP4FnVPQZwRmrDyIIebA5y-ynoXywt9lihThMLlEsCh55hA')

# функция запроса дополнительной информации у пользователя
def request_info(user_id):
    vk_session.method('messages.send', {'user_id': user_id, 'message': 'Для поиска нужна дополнительная информация. Укажите свой возраст:'})
    age = vk_session.method('messages.getHistory', {'user_id': user_id, 'count': 1})['items'][0]['text']
    vk_session.method('messages.send', {'user_id': user_id, 'message': 'Укажите пол (м/ж):'})
    sex = vk_session.method('messages.getHistory', {'user_id': user_id, 'count': 1})['items'][0]['text']
    vk_session.method('messages.send', {'user_id': user_id, 'message': 'Укажите город (название или id):'})
    city = vk_session.method('messages.getHistory', {'user_id': user_id, 'count': 1})['items'][0]['text']
    vk_session.method('messages.send', {'user_id': user_id, 'message': 'Укажите семейное положение (необязательно):'})
    relationship = vk_session.method('messages.getHistory', {'user_id': user_id, 'count': 1})['items'][0]['text']
    vk_session.method('messages.send', {'user_id': user_id, 'message': 'Укажите интересы (необязательно):'})
    interests = vk_session.method('messages.getHistory', {'user_id': user_id, 'count': 1})['items'][0]['text']
    return age, sex, city, relationship, interests

# функция поиска пользователей
def find_users(age, sex, city, relationship, interests, partner_sex, partner_age):
    # получение списка пользователей, удовлетворяющих заданным условиям
    users = vk_session.method('users.search', {'count': 20, 'age_from': partner_age[0], 'age_to': partner_age[1], 'sex': partner_sex, 'city': city, 'status': relationship})['items']
    # формирование списка найденных пользователей
    results = []
    for user in users:
        # фильтрация по интересам и хобби
        if interests:
            user_groups = vk_session.method('groups.get', {'user_id': user['id'], 'count': 1000})['items']
            if not any(interest.lower() in group['name'].lower() for interest in interests.split(',') for group in user_groups):
                continue
        # получение топ-3 популярных фотографий профиля
        photos = vk_session.method('photos.get', {'owner_id': user['id'], 'album_id': 'profile', 'extended': 1, 'count': 3})['items']
        photos_info = []
        for photo in photos:
            photos_info.append({'likes': photo['likes']['count'] + photo['comments']['count'], 'url': photo['sizes'][-1]['url']})
        photos_info.sort(key=lambda x: x['likes'], reverse=True)
        top_photos = [photo['url'] for photo in photos_info[:3]]
        # формирование сообщения с информацией о найденном пользователе и топ-3 фото
        message = f"{user['first_name']} {user['last_name']}, {user['age']} лет, {user['city']['title']}, {user['relation']}\n"
        top_3_photo = "Топ-3 популярных фото профиля:'\n{'\n'.join(top_photos)}"
        message += f"{top_3_photo}"

        results.append({'message': message, 'user_id': user['id']})
    return results

# функция отправки результатов поиска пользователю
def send_results(user_id, results):
    # формирование сообщения с результатами поиска
    message = "Результаты поиска:\n"
    for result in results:
        message += f"{result['message']}\nhttps://vk.com/id{result['user_id']}\n\n"
    # отправка сообщения пользователю
    vk_session.method('messages.send', {'user_id': user_id, 'message': message})

# основная функция бота
def main():
    # получение информации о пользователе
    user_id = '243617277'
    user_info = vk_session.method('users.get', {'user_ids': user_id, 'fields': 'bdate, sex, city, relation'})[0]
    #