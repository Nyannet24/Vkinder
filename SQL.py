#import sqlite3 # Тестировалось на БД SQLite3
import psycopg2
from math import radians, cos, sin, asin, sqrt
from datetime import date


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
            cursor.executescript("""CREATE TABLE IF NOT EXISTS Users (
                                        ID INTEGER PRIMARY KEY,
                                        Sex INTEGER,
                                        Age INTEGER,
                                        Latitude  TEXT,
                                        Longitude TEXT,
                                        City TEXT,
                                        ActiveProfile BOOLEAN,
                                        Pair INTEGER);
                                    
                                    CREATE TABLE IF NOT EXISTS Match (
                                        ID_me INTEGER,
                                        ID_pair INTEGER,
                                        Result BOOLEAN,
                                        Date TEXT);
                                 """)
        #print("БД создана")

###### Работа с пользователем

    # Создание пользователя
    def CreateUser(self, User): 
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"INSERT OR IGNORE INTO Users (ID, Sex, Age, Latitude, Longitude, City, ActiveProfile) VALUES ('{User[0]}', '{User[1]}', '{User[2]}', '{User[3]}', '{User[4]}', '{User[5]}', '1');")
            
    # Обновление пользователя
    def UpdateUser(self, ID, Sex, Age, Latitude, Longitude, City): 
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"""UPDATE Users
                  SET Sex = {Sex},
                      Age = {Age},
                      Latitude = '{Latitude}',
                      Longitude = '{Longitude}',
                      City = '{City}'
                  WHERE ID = {ID}
                  ;""")

    # Проверка существования пользователя в Базе Данных
    def CheckUser(self, User): 
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT EXISTS(SELECT 1 FROM Users WHERE ID = ?)", (User,))
            result = cursor.fetchone()[0]
            return bool(result)

    # Получение профиля
    def GetUser(self, ID):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM Users WHERE ID = {ID}")
            result = cursor.fetchone()
            return result

    # Установка активности профиля
    def SetUserActive(self, ID, Active): 
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE Users SET ActiveProfile = ? WHERE ID = ?", (Active, ID))

    # Получение активности анкеты
    def GetUserActive(self, ID):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT ActiveProfile FROM Users WHERE ID = {ID}")
            result = cursor.fetchone()[0]
            return result

    # Установка пары в профиль
    def SetUserPair(self, ID, Pair):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE Users SET Pair = {Pair} WHERE ID = {ID}")

    # Получение пары из профиля
    def GetUserPair(self, ID):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT Pair FROM Users WHERE ID = {ID}")
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


###### Работа с табличей мэтчей
    
    # Получение записи мэтча
    def SetMatchHistory(self, MyID, PairID, Result):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"INSERT INTO Match (ID_me, ID_pair, Result, Date) VALUES ('{MyID}', '{PairID}', {Result}, '{date.today()}');")

    # Удаление записи из мэтча
    def DeleteMatchHistory(self, Days):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM Match WHERE DATE(Date) <= DATE('now', '-{Days} days');")


###### Работа с поиском анкет

    # Главный запрос на поиск подходящей анкеты
    def SearchPair(self, MyID, Sex, Age):
        # 1 Указывает на активность профиля. 3 указывает на допустимую разницу между возрастами.
        # В сравнении 20 является 20 км. Это означает, что пользователю будут отображаться
        # профили в пределах 20 км. Данный запрос в будущем можно будет модернизировать и
        # каждому пользователю позволить выбирать свой радиус поиска анкет и разницу возраста.
        SearchSex = 1 if Sex == 2 else 2
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"""SELECT ID
                                FROM Users
                                WHERE ActiveProfile = 1
                                    AND Sex = {SearchSex}
                                    AND ABS(Age - {Age}) <= 3
                                    AND ID NOT IN (
                                        SELECT ID_pair
                                        FROM Match
                                        WHERE ID_me = {MyID}
                                    )
                                    AND (
                                        6371 * 2 * ASIN(
                                            SQRT(
                                                POWER(SIN(RADIANS((SELECT Latitude FROM Users WHERE ID = {MyID})) - CAST(Latitude AS REAL)) / 2, 2) +
                                                COS(RADIANS(CAST(Latitude AS REAL))) * COS(RADIANS((SELECT Latitude FROM Users WHERE ID = {MyID}))) *
                                                POWER(SIN(RADIANS((SELECT Longitude FROM Users WHERE ID = {MyID})) - CAST(Longitude AS REAL)) / 2, 2)
                                            )
                                        )
                                    ) <= 20
                                LIMIT 1
                                ;""")
            
                            
            result = cursor.fetchone()
            return result

    # Вспомогательная функция для поиска дистанции
    def haversine_distance(self, lat1, lon1, lat2, lon2): 
        # Преобразование координат из градусов в радианы
        lat1_rad, lon1_rad = radians(float(lat1)), radians(float(lon1))
        lat2_rad, lon2_rad = radians(float(lat2)), radians(float(lon2))
        # Разница координат
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        # Формула гаверсинусов
        a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        # Радиус Земли в километрах
        radius = 6371
        # Вычисляем расстояние и возвращаем
        return c * radius

    # Функция для поиска дистанции
    def SearchDistance(self, MyID, PairID):
        with self.connection:
            cursor = self.connection.cursor()
            # Получение координат первого пользователя
            cursor.execute(f"SELECT Latitude, Longitude FROM Users WHERE ID = {MyID}")
            result1 = cursor.fetchone()
            lat1, lon1 = result1
            # Получение координат второго пользователя
            cursor.execute(f"SELECT Latitude, Longitude FROM Users WHERE ID = {PairID}")
            result2 = cursor.fetchone()
            lat2, lon2 = result2
            # Вычисление расстояния
            return self.haversine_distance(lat1, lon1, lat2, lon2)
