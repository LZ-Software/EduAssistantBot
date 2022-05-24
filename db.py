import sqlite3

from log import Logger


def read(filename):
    with open(filename, 'r') as f:
        return f.read()


class DB:

    __connection = None

    def __init__(self):
        self.connection = sqlite3.connect('mirea-assistant.db')

    def __get_group_count(self):
        try:
            cursor = self.connection.cursor()
            cmd = 'SELECT COUNT(*) FROM StudyGroup'
            cursor.execute(cmd)
            records = cursor.fetchall()
            count = records[0][0]
            Logger.ok(f'ГРУППЫ В БАЗЕ [{count}]')
            return count
        except sqlite3.DatabaseError:
            Logger.error(f'ОШИБКА ПОЛУЧЕНИЯ ГРУПП ИЗ БАЗЫ')
            return 0

    def __get_schedule_count(self):
        try:
            cursor = self.connection.cursor()
            cmd = 'SELECT COUNT(*) FROM Schedule'
            cursor.execute(cmd)
            records = cursor.fetchall()
            count = records[0][0]
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
            cursor = self.connection.cursor()
            cmd = 'INSERT INTO Days(day_number) VALUES (:d)'
            cursor.execute(cmd, {'d': day})
            self.connection.commit()
            Logger.ok(f'ДЕНЬ [{day}] ДОБАВЛЕН')
        except sqlite3.DatabaseError:
            Logger.error(f'ДЕНЬ [{day}] НЕ ДОБАВЛЕН')

    def __add_week(self, week):
        try:
            cursor = self.connection.cursor()
            cmd = 'INSERT INTO Week(parity) VALUES (:p)'
            cursor.execute(cmd, {'p': week})
            self.connection.commit()
            Logger.ok(f'НЕДЕЛЯ [{week}] ДОБАВЛЕНА')
        except sqlite3.DatabaseError:
            Logger.error(f'НЕДЕЛЯ [{week}] НЕ ДОБАВЛЕНА')

    def create_db_if_not_exists(self):
        cursor = self.connection.cursor()
        cursor.executescript(read('request.txt'))
        self.connection.commit()
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
            cursor = self.connection.cursor()
            cmd = 'INSERT INTO StudyGroup(name) VALUES (?)'
            cursor.execute(cmd, [group])
            self.connection.commit()
            Logger.ok(f'ГРУППА [{group}] ДОБАВЛЕНА')
        except sqlite3.DatabaseError:
            Logger.error(f'ГРУППА [{group}] НЕ ДОБАВЛЕНА')
            raise StopIteration

    def add_schedule(self, group, para, day, week, subject, subject_type, teacher, auditorium):
        try:
            cursor = self.connection.cursor()
            request = 'INSERT INTO Schedule(group_id, para, day_id, week_id, subject, subject_type, teacher, auditorium) ' \
                      'VALUES ((SELECT id FROM StudyGroup WHERE name = ?), ?, (SELECT id FROM Days WHERE day_number = ?), ' \
                      '(SELECT id FROM Week WHERE parity = ?), ?, ?, ?, ?)'
            data = [group, para, day, week, subject, subject_type, teacher, auditorium]
            cursor.execute(request, data)
            self.connection.commit()
        except sqlite3.DatabaseError:
            if week == 0:
                w = 'ЧЕТНАЯ'
            elif week == 1:
                w = 'НЕЧЕТНАЯ'
            else:
                w = '?'
            Logger.error(f'ГРУППА [{group}] НЕДЕЛЯ [{w}] ДЕНЬ [{day}] ПАРА [{para}] - ОШИБКА')

    def close_connection(self):
        self.connection.close()
