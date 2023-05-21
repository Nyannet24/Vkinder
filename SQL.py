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
        except (Exception, psycopg2.Error) as error:
            print(f"При подключении к базе данных произошла ошибка: {error}")

    # Создание таблиц в базе данных
    def SetDB(self): 
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS Users (
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
        #print("БД создана")

###### Работа с пользователем

    # Создание пользователя
    def CreateUser(self, User): 
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"INSERT OR IGNORE INTO Users (ID, Sex, Age, City, Relation, Offset) VALUES ('{User[0]}', '{User[1]}', '{User[2]}', '{User[3]}', '{User[4]}', 0);")
            
    # Обновление пользователя
    def UpdateUser(self, User): 
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"""UPDATE Users
                  SET Sex = '{User[1]}',
                      Age = '{User[2]}',
                      City = '{User[3]}',
                      Relation = '{User[4]}'
                  WHERE ID = '{User[0]}'
                  ;""")

    # Проверка существования пользователя в Базе Данных
    def CheckUser(self, User): 
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT EXISTS(SELECT 1 FROM Users WHERE ID = {User})")
            result = cursor.fetchone()[0]
            return bool(result)

    # Получение профиля
    def GetUser(self, ID):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT Sex, Age, City FROM Users WHERE ID = {ID}")
            result = cursor.fetchone()
            return result

    # Установка смещения
    def SetUserOffset(self, ID, Offset): 
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE Users SET Offset = {Offset} WHERE ID = {ID}")

    # Автоинкрементирование смещения
    def AddUserOffset(self, ID): 
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE Users SET Offset = Offset + 1 WHERE ID = {ID}")

    # Получение смещения
    def GetUserOffset(self, ID):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT Offset FROM Users WHERE ID = {ID}")
            result = cursor.fetchone()[0]
            return result

    # Установка количества найденных подходящих анкет
    def SetUserMax(self, ID, Max):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE Users SET Max = {Max} WHERE ID = {ID}")

    # Получение количества найденных подходящих анкет
    def GetUserMax(self, ID):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT Max FROM Users WHERE ID = {ID}")
            result = cursor.fetchone()[0]
            return result

    # Установка пары в профиль
    def SetUserItems(self, ID, Items):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE Users SET Items = {Items} WHERE ID = {ID}")

    # Получение пары из профиля
    def GetUserItems(self, ID):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT Items FROM Users WHERE ID = {ID}")
            result = cursor.fetchone()[0]
            return result

    # Установка возраста в профиле
    def SetUserAge(self, ID, Age):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE Users SET Age = {Age} WHERE ID = {ID}")

    # Получение возраста в профиле
    def GetUserAge(self, ID):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT Age FROM Users WHERE ID = {ID}")
            result = cursor.fetchone()[0]
            return result


###### Работа с таблицей Match
    
    # Создание записи в Match
    def SetMatchHistory(self, PairID, Result):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"INSERT INTO Match (ID_pair, Result, Date) VALUES ('{PairID}', {Result}, '{date.today()}');")
    
    # Получение записи из Match
    def GetCountMatchFromPair(self, ID_pair):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM Match WHERE ID_pair = {ID_pair};")
            result = cursor.fetchone()[0]
            return result == 0

    # Удаление всех записей из Match
    def DeleteMatchHistory(self):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM Match;")