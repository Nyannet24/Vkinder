import psycopg2
from datetime import date
#import sqlite3 # Тестировалось на БД SQLite3
#from math import radians, cos, sin, asin, sqrt

class SQL:

    # Инициализирующая функция
    def __init__(self):
        #self.connection = sqlite3.connect('database.db') # Тестировалось на БД SQLite3
        try:
            # Указываем данные для подключения к базе данных
            self.connection = psycopg2.connect(
                host="host",
                port="port",
                database="database",
                user="user",
                password="password"
            )
            print("Успешное подключение к базе данных")
        except (Exception, psycopg2.Error) as err:
            print(f"При подключении к базе данных произошла ошибка: {err}")

    # Создание таблиц в базе данных
    def set_db(self): 
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS User (
                                        ID INTEGER PRIMARY KEY,
                                        Sex INTEGER,
                                        Age INTEGER,
                                        City INTEGER,
                                        Relation TEXT,
                                        Items TEXT,
                                        Offset INTEGER,
                                        Max INTEGER);""")
                                    
            cursor.execute("""CREATE TABLE IF NOT EXISTS Match (
                                        ID_pair INTEGER,
                                        Result BOOLEAN,
                                        Date TEXT);""")
                                    
            cursor.execute("""CREATE TABLE IF NOT EXISTS FoundUsers (
                                        UserID INTEGER,
                                        Name TEXT,
                                        Relation INTEGER,
                                        Profile BOOLEAN);""")
        #print("БД создана")


###### Работа со всеми пользователями

    # Создание пользователя
    def create_found(self, user): 
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"INSERT OR IGNORE INTO FoundUsers (UserID, Name, Relation, Profile) VALUES ('{user[0]}', '{user[1]}', '{user[2]}', '{user[3]}');")
            
    # Получение количества текущей "партии" пользователей на оценку
    def get_count_found(self):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM FoundUsers;")
            result = cursor.fetchone()[0]
            return result == 0

    # Получение конкретного пользователе в размере 1 из "партии" на оценку
    def get_found(self):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM FoundUsers LIMIT 1")
            result = cursor.fetchone()
            return result

    # Удаление оцененного пользователя из "партии"
    def delete_found(self, found_id):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM FoundUsers WHERE UserID = {found_id};")



###### Работа с основным пользователем

    # Создание пользователя
    def create_user(self, user): 
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"INSERT OR IGNORE INTO User (ID, Sex, Age, City, Relation, Offset) VALUES ('{user[0]}', '{user[1]}', '{user[2]}', '{user[3]}', '{user[4]}', 0);")
            
    # Обновление пользователя
    def update_user(self, user): 
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"""UPDATE User
                  SET Sex = '{user[1]}',
                      Age = '{user[2]}',
                      City = '{user[3]}',
                      Relation = '{user[4]}'
                  WHERE ID = '{user[0]}'
                  ;""")

    # Проверка существования пользователя в Базе Данных
    def check_user(self, user): 
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT EXISTS(SELECT 1 FROM User WHERE ID = {user})")
            result = cursor.fetchone()[0]
            return bool(result)

    # Получение профиля
    def get_user(self, ID):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT Sex, Age, City FROM User WHERE ID = {ID}")
            result = cursor.fetchone()
            return result

    # Установка смещения
    def set_user_offset(self, ID, offset): 
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE User SET Offset = {offset} WHERE ID = {ID}")

    # Увеличение смещения на 50
    def add_user_offset(self, ID): 
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE User SET Offset = Offset + 50 WHERE ID = {ID}")

    # Получение смещения
    def get_user_offset(self, ID):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT Offset FROM User WHERE ID = {ID}")
            result = cursor.fetchone()[0]
            return result

    # Установка количества найденных подходящих анкет
    def set_user_max(self, ID, Max):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE User SET Max = {Max} WHERE ID = {ID}")

    # Получение количества найденных подходящих анкет
    def get_user_max(self, ID):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT Max FROM User WHERE ID = {ID}")
            result = cursor.fetchone()[0]
            return result

    # Установка пары в профиль
    def set_user_items(self, ID, items):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE User SET Items = {items} WHERE ID = {ID}")

    # Получение пары из профиля
    def get_user_items(self, ID):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT Items FROM User WHERE ID = {ID}")
            result = cursor.fetchone()[0]
            return result

    # Установка возраста в профиле
    def set_user_age(self, ID, age):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE User SET Age = {age} WHERE ID = {ID}")

    # Получение возраста в профиле
    def get_user_age(self, ID):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT Age FROM User WHERE ID = {ID}")
            result = cursor.fetchone()[0]
            return result


###### Работа с таблицей Match
    
    # Создание записи в Match
    def set_match_history(self, pair_id, result):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"INSERT INTO Match (ID_pair, Result, Date) VALUES ('{pair_id}', {result}, '{date.today()}');")
    
    # Получение записи из Match
    def get_count_match_from_pair(self, pair_id):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM Match WHERE ID_pair = {pair_id};")
            result = cursor.fetchone()[0]
            return result == 0

    # Удаление всех записей из Match
    def delete_match_history(self):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM Match;")