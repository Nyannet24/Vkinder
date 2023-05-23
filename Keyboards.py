from vk_api.keyboard import VkKeyboard, VkKeyboardColor

class Keyboards:
    # Клавиатура меню
    def Menu(self):
        keyboard = VkKeyboard(one_time=True)  # one_time=True для скрытия клавиатуры после использования
        keyboard.add_button('Поиск', color=VkKeyboardColor.POSITIVE)
        # Добавление новой строки для расположения кнопок в несколько столбцов
        keyboard.add_line()  
        keyboard.add_button('Обновить профиль', color=VkKeyboardColor.POSITIVE)
        return keyboard

    # Клавиатура создания профиля
    def Create(self):
        keyboard = VkKeyboard(one_time=True)  # one_time=True для скрытия клавиатуры после использования
        keyboard.add_button('Создать профиль', color=VkKeyboardColor.POSITIVE)
        return keyboard

    # Клавиатура при поиске анкет
    def SearchPair(self):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Лайк', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Дизлайк', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Уйти в меню', color=VkKeyboardColor.NEGATIVE)
        return keyboard

    # Клавиатура подтверждения после лайка
    def SearchPairContinue(self):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Уйти в меню', color=VkKeyboardColor.NEGATIVE)
        return keyboard
