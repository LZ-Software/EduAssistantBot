import sqlite3

from log import Logger


def read(filename):
    with open(filename, 'r') as f:
        return f.read()


class DB:

    __connection = None

    def __init__(self):
        self.__connection = sqlite3.connect('mirea-assistant.db', check_same_thread=False)
        self.__create_db_if_not_exists()

    def __get_group_count(self):
        try:
            cursor = self.__connection.cursor()
            cmd = 'SELECT COUNT(*) FROM StudyGroup'
            cursor.execute(cmd)
            record = cursor.fetchone()
            count = record[0]
            if count == 0:
                Logger.error(f'ГРУППЫ В БАЗЕ [{count}]')
            else:
                Logger.ok(f'ГРУППЫ В БАЗЕ [{count}]')
            return count
        except sqlite3.DatabaseError:
            Logger.error(f'ОШИБКА ПОЛУЧЕНИЯ ГРУПП ИЗ БАЗЫ')
            return 0

    def __get_schedule_count(self):
        try:
            cursor = self.__connection.cursor()
            cmd = 'SELECT COUNT(*) FROM Schedule'
            cursor.execute(cmd)
            record = cursor.fetchone()
            count = record[0]
            if count == 0:
                Logger.error(f'ЗАПИСЕЙ РАСПИСАНИЯ В БАЗЕ [{count}]')
            else:
                Logger.ok(f'ЗАПИСЕЙ РАСПИСАНИЯ В БАЗЕ [{count}]')
            return count
        except sqlite3.DatabaseError:
            Logger.error(f'ОШИБКА ПОЛУЧЕНИЯ РАСПИСАНИЯ ИЗ БАЗЫ')
            return 0

    def __init_week(self):
        self.__add_week(0)
        self.__add_week(1)

    def __init_days(self):
        for i in range(1, 7):
            self.__add_day(i)

    def __add_day(self, day):
        try:
            cursor = self.__connection.cursor()
            cmd = 'INSERT INTO Days(day_number) VALUES (:d)'
            cursor.execute(cmd, {'d': day})
            self.__connection.commit()
            Logger.ok(f'ДЕНЬ [{day}] ДОБАВЛЕН')
        except sqlite3.DatabaseError:
            Logger.error(f'ДЕНЬ [{day}] НЕ ДОБАВЛЕН')

    def __add_week(self, week):
        try:
            cursor = self.__connection.cursor()
            cmd = 'INSERT INTO Week(parity) VALUES (:p)'
            cursor.execute(cmd, {'p': week})
            self.__connection.commit()
            Logger.ok(f'НЕДЕЛЯ [{week}] ДОБАВЛЕНА')
        except sqlite3.DatabaseError:
            Logger.error(f'НЕДЕЛЯ [{week}] НЕ ДОБАВЛЕНА')

    def __create_db_if_not_exists(self):
        cursor = self.__connection.cursor()
        cursor.executescript(read('request.txt'))
        self.__connection.commit()
        self.__init_week()
        self.__init_days()

    def has_records(self):
        groups = self.__get_group_count()
        schedule = self.__get_schedule_count()
        try:
            if schedule / groups == 72:
                return True
            else:
                return False
        except ZeroDivisionError:
            return False

    def add_group(self, group):
        try:
            cursor = self.__connection.cursor()
            cmd = 'INSERT INTO StudyGroup(name) VALUES (:g)'
            cursor.execute(cmd, {'g': group})
            self.__connection.commit()
            Logger.ok(f'ГРУППА [{group}] ДОБАВЛЕНА')
        except sqlite3.DatabaseError:
            Logger.error(f'ГРУППА [{group}] НЕ ДОБАВЛЕНА')
            raise StopIteration

    def add_schedule(self, group, para, day, week, subject, subject_type, teacher, auditorium):
        try:
            cursor = self.__connection.cursor()
            request = 'INSERT INTO Schedule(group_id, para, day_id, week_id, subject, subject_type,' \
                      ' teacher, auditorium) VALUES ((SELECT id FROM StudyGroup WHERE name = ?), ?, (SELECT id FROM ' \
                      'Days WHERE day_number = ?), (SELECT id FROM Week WHERE parity = ?), ?, ?, ?, ?)'
            data = [group, para, day, week, subject, subject_type, teacher, auditorium]
            cursor.execute(request, data)
            self.__connection.commit()
        except sqlite3.DatabaseError:
            if week == 0:
                w = 'ЧЕТНАЯ'
            elif week == 1:
                w = 'НЕЧЕТНАЯ'
            else:
                w = '?'
            Logger.error(f'ГРУППА [{group}] НЕДЕЛЯ [{w}] ДЕНЬ [{day}] ПАРА [{para}] - ОШИБКА')

    def add_user(self, user_id, name):
        try:
            cursor = self.__connection.cursor()
            cmd = 'INSERT INTO Users(user_id, name) VALUES (:uid, :n)'
            cursor.execute(cmd, {'uid': user_id, 'n': name})
            self.__connection.commit()
            Logger.ok(f'ПОЛЬЗОВАТЕЛЬ ДОБАВЛЕН В БАЗУ [{user_id}]')
            return True
        except sqlite3.DatabaseError:
            Logger.error(f'ОШИБКА ДОБАВЛЕНИЯ ПОЛЬЗОВАТЕЛЯ В БАЗУ [{user_id}]')
            return False

    def get_user(self, user_id):
        try:
            user = dict()
            cursor = self.__connection.cursor()
            cmd = 'SELECT * FROM Users WHERE user_id = :user_id'
            cursor.execute(cmd, {'user_id': user_id})
            record = cursor.fetchone()
            if record is None:
                Logger.error(f'ОШИБКА ПОЛУЧЕНИЯ ПОЛЬЗОВАТЕЛЯ ИЗ БАЗЫ [{user_id}]')
                return None
            tid = record[1]
            name = record[2]
            user['tid'] = tid
            user['name'] = name
            Logger.ok(f'ПОЛЬЗОВАТЕЛЬ ПОЛУЧЕН ИЗ БАЗЫ ПРИ ПОВТОРНОМ ОБРАЩЕНИИ [{tid}]')
            return user
        except sqlite3.DatabaseError:
            Logger.error(f'ОШИБКА ПОЛУЧЕНИЯ ПОЛЬЗОВАТЕЛЯ ИЗ БАЗЫ [{user_id}]')
            return None

    def get_group_id(self, group_name):
        try:
            cursor = self.__connection.cursor()
            cmd = 'SELECT * FROM StudyGroup WHERE name = :group_name'
            cursor.execute(cmd, {'group_name': group_name})
            record = cursor.fetchone()
            if record is None:
                Logger.error(f'ОШИБКА ПОЛУЧЕНИЯ ГРУППЫ ИЗ БАЗЫ [{group_name}]')
                return False, -1
            else:
                gid = record[0]
                Logger.ok(f'ГРУППА ПОЛУЧЕНА ИЗ БАЗЫ ПРИ ОБРАЩЕНИИ [{group_name}] [{gid}]')
                return True, gid
        except sqlite3.DatabaseError:
            Logger.error(f'ОШИБКА ПОЛУЧЕНИЯ ГРУППЫ ИЗ БАЗЫ [{group_name}]')
            return False, -1

    def subscribe_user(self, user_id, group_id):
        try:
            cursor = self.__connection.cursor()
            cmd = 'INSERT INTO User_To_Group(user_id, group_id) VALUES (:user_id, :group_id)'
            cursor.execute(cmd, {'user_id': user_id, 'group_id': group_id})
            self.__connection.commit()
            Logger.ok(f'ПОЛЬЗОВАТЕЛЬ СВЯЗАН С ГРУППОЙ [{user_id}] [{group_id}]')
            return True
        except sqlite3.DatabaseError:
            Logger.error(f'ОШИБКА СВЯЗЫВАНИЯ ПОЛЬЗОВАТЕЛЯ С ГРУППОЙ [{user_id}] [{group_id}]')
            return False

    def unsubscribe_user(self, user_id):
        try:
            cursor = self.__connection.cursor()
            cmd = 'DELETE FROM User_To_Group WHERE user_id = :user_id'
            cursor.execute(cmd, {'user_id': user_id})
            self.__connection.commit()
            cmd = 'DELETE FROM Users WHERE user_id = :user_id'
            cursor.execute(cmd, {'user_id': user_id})
            self.__connection.commit()
            Logger.ok(f'ПОЛЬЗОВАТЕЛЬ ОТВЯЗАН ОТ ГРУППЫ [{user_id}]')
        except sqlite3.DatabaseError:
            Logger.error(f'ОШИБКА ОТВЯЗКИ ПОЛЬЗОВАТЕЛЯ ОТ ГРУППЫ [{user_id}]')

    def close_connection(self):
        self.__connection.close()
