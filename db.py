import sqlite3

from log import Logger
from date import Date


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
                Logger.error(f'ГРУППЫ В БАЗЕ - [{count}]')
            else:
                Logger.ok(f'ГРУППЫ В БАЗЕ - [{count}]')
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
                Logger.error(f'ЗАПИСЕЙ РАСПИСАНИЯ В БАЗЕ - [{count}]')
            else:
                Logger.ok(f'ЗАПИСЕЙ РАСПИСАНИЯ В БАЗЕ - [{count}]')
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
            Logger.ok(f'ДЕНЬ[{day}] ДОБАВЛЕН')
        except sqlite3.DatabaseError:
            Logger.error(f'ДЕНЬ[{day}] НЕ ДОБАВЛЕН')

    def __add_week(self, week):
        try:
            cursor = self.__connection.cursor()
            cmd = 'INSERT INTO Week(parity) VALUES (:p)'
            cursor.execute(cmd, {'p': week})
            self.__connection.commit()
            Logger.ok(f'НЕДЕЛЯ[{week}] ДОБАВЛЕНА')
        except sqlite3.DatabaseError:
            Logger.error(f'НЕДЕЛЯ[{week}] НЕ ДОБАВЛЕНА')

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
            Logger.ok(f'ГРУППА ДОБАВЛЕНА - [{group}]')
        except sqlite3.DatabaseError:
            Logger.error(f'ГРУППА НЕ ДОБАВЛЕНА - [{group}]')
            raise StopIteration

    def add_schedule(self, group, para, day, week, subject, subject_type, teacher, auditorium):
        try:
            cursor = self.__connection.cursor()
            request = '''INSERT INTO Schedule(group_id, para, day_id, week_id, subject, subject_type, teacher, 
                         auditorium)
                         VALUES ((SELECT id FROM StudyGroup WHERE name = ?), ?, 
                         (SELECT id FROM Days WHERE day_number = ?), 
                         (SELECT id FROM Week WHERE parity = ?), ?, ?, ?, ?)'''
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
            Logger.error(f'ОШИБКА РАСПИСАНИЯ - ГРУППА[{group}] НЕДЕЛЯ[{w}] ДЕНЬ[{day}] ПАРА[{para}]')

    def add_user(self, user_id, name):
        try:
            cursor = self.__connection.cursor()
            cmd = 'INSERT INTO Users(user_id, name) VALUES (:uid, :n)'
            cursor.execute(cmd, {'uid': user_id, 'n': name})
            self.__connection.commit()
            Logger.ok(f'ПОЛЬЗОВАТЕЛЬ ДОБАВЛЕН - [{user_id}]')
            return True
        except sqlite3.DatabaseError:
            Logger.error(f'ПОЛЬЗОВАТЕЛЬ НЕ ДОБАВЛЕН - [{user_id}]')
            return False

    def get_user(self, user_id):
        try:
            user = dict()
            cursor = self.__connection.cursor()
            cmd = 'SELECT * FROM Users WHERE user_id = :user_id'
            cursor.execute(cmd, {'user_id': user_id})
            record = cursor.fetchone()
            if record is None:
                Logger.error(f'ПОЛЬЗОВАТЕЛЬ НЕ ПОЛУЧЕН - [{user_id}]')
                return None
            tid = record[1]
            name = record[2]
            user['tid'] = tid
            user['name'] = name
            Logger.ok(f'ПОЛЬЗОВАТЕЛЬ ПОЛУЧЕН - [{tid}]')
            return user
        except sqlite3.DatabaseError:
            Logger.error(f'ПОЛЬЗОВАТЕЛЬ НЕ ПОЛУЧЕН - [{user_id}]')
            return None

    def get_group_id(self, group_name):
        try:
            cursor = self.__connection.cursor()
            cmd = 'SELECT * FROM StudyGroup WHERE name = :group_name'
            cursor.execute(cmd, {'group_name': group_name})
            record = cursor.fetchone()
            if record is None:
                Logger.error(f'ГРУППА ПОЛУЧЕНА - [{group_name}]')
                return False, -1
            else:
                gid = record[0]
                Logger.ok(f'ГРУППА НЕ ПОЛУЧЕНА - [{group_name}] [{gid}]')
                return True, gid
        except sqlite3.DatabaseError:
            Logger.error(f'ГРУППА ПОЛУЧЕНА - [{group_name}]')
            return False, -1

    def get_user_group_id(self, user_id):
        try:
            cursor = self.__connection.cursor()
            cmd = 'SELECT group_id FROM User_To_Group WHERE user_id = :uid'
            cursor.execute(cmd, {'uid': user_id})
            record = cursor.fetchone()
            gid = record[0]
            Logger.ok(f'ГРУППА ПОЛЬЗОВАТЕЛЯ ПОЛУЧЕНА - [{user_id}] [{gid}]')
            return gid
        except sqlite3.DatabaseError:
            Logger.error(f'ГРУППА ПОЛЬЗОВАТЕЛЯ НЕ ПОЛУЧЕНА - [{user_id}]')
            return None

    def subscribe_user(self, user_id, group_id):
        try:
            cursor = self.__connection.cursor()
            cmd = 'INSERT INTO User_To_Group(user_id, group_id) VALUES (:user_id, :group_id)'
            cursor.execute(cmd, {'user_id': user_id, 'group_id': group_id})
            self.__connection.commit()
            Logger.ok(f'ПОЛЬЗОВАТЕЛЬ ПРИВЯЗАН К ГРУППЕ - [{user_id}] [{group_id}]')
            return True
        except sqlite3.DatabaseError:
            Logger.error(f'ПОЛЬЗОВАТЕЛЬ НЕ ПРИВЯЗАН К ГРУППЕ - [{user_id}] [{group_id}]')
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
            Logger.ok(f'ПОЛЬЗОВАТЕЛЬ ОТВЯЗАН ОТ ГРУППЫ - [{user_id}]')
        except sqlite3.DatabaseError:
            Logger.error(f'ПОЛЬЗОВАТЕЛЬ НЕ ОТВЯЗАН ОТ ГРУППЫ - [{user_id}]')

    def get_day_schedule(self, group_id, parity, day_id, shift=0, all_week=False):
        if day_id == 6 and shift == 1 and not all_week:  # Сегодня суббота, а расписание на завтра (воскресенье)
            day = Date.get_formatted_date_title(shift)
            return day + '<pre>Выходной день</pre>'
        elif day_id == 7 and (shift == 0 or all_week):  # Сегодня воскресенье, и расписание на сегодня (воскресенье)
            day = Date.get_formatted_date_title(shift)
            return day + '<pre>Выходной день</pre>'
        elif day_id == 7 and shift == 1:  # Сегодня воскресенье, а расписание на завтра (понедельник)
            day_id = 1
            if parity == 0:
                parity = 1
            else:
                parity = 0
            day = Date.get_formatted_date_title(shift, 1)
        else:  # Нормальные дни
            if all_week:
                day = Date.get_formatted_date_title(shift)
            else:
                day = Date.get_formatted_date_title(shift)
                day_id = day_id + shift
        try:
            cursor = self.__connection.cursor()
            cmd = '''SELECT s.para, s.subject, s.subject_type, s.teacher, s.auditorium FROM Schedule s
                     JOIN StudyGroup g ON g.id = s.group_id 
                     JOIN Days d ON d.id = s.day_id 
                     JOIN Week w ON w.id = s.week_id 
                     WHERE g.id = :gid AND w.parity = :p AND d.id = :did'''
            cursor.execute(cmd, {'gid': group_id, 'p': parity, 'did': day_id})
            records = cursor.fetchall()
            text = ''
            dash_count = 0
            for row in records:  # Проверяем, если день выходной
                if row[1] == '-':
                    dash_count = dash_count + 1
            if dash_count == 6:
                return day + '<pre>Выходной день</pre>'
            for row in records:
                para = row[0]
                subject = row[1]
                st = row[2]
                teacher = row[3]
                cab = row[4]
                if subject == '-':  # Проверяем, если пары нету
                    continue
                txt = f'<b>({para} пара)</b> <i>[{st}]</i>\n<u>{subject}</u>\n<pre>{teacher}</pre>\n<b>{cab}</b>\n\n'
                text = text + txt
            Logger.ok(f'РАСПИСАНИЕ ПОЛУЧЕНО - ГРУППА[{group_id}] ДЕНЬ[{day_id}] ЧЕТНОСТЬ[{parity}]')
            return day + text
        except sqlite3.DatabaseError:
            Logger.error(f'РАСПИСАНИЕ ПОЛУЧЕНО - ГРУППА[{group_id}] ДЕНЬ[{day_id}] ЧЕТНОСТЬ[{parity}]')

    def get_week_schedule(self, group_id, next_week=False):
        ret = list()
        parity = Date.get_parity()
        if next_week:
            current_day = 1
            if parity == 0:
                parity = 1
            else:
                parity = 0
        else:
            current_day = Date.get_day_number()
        shift = 0
        for current_day in range(current_day, 8):
            res = self.get_day_schedule(group_id, parity, current_day, shift, all_week=True)
            ret.append(res)
            shift = shift + 1
        return ret

    def close_connection(self):
        self.__connection.close()
