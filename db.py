import sqlite3


def read(filename):
    with open(filename, 'r') as f:
        return f.read()


class DB:
    connection = None

    def __init__(self):
        self.connection = sqlite3.connect('mirea-assistant.db')

    def create_db(self):
        cursor = self.connection.cursor()
        cursor.executescript(read('request.txt'))
        self.connection.commit()

    def close_connection(self):
        self.connection.close()

    def add_group(self, group):
        cursor = self.connection.cursor()
        cmd = 'INSERT INTO Grups(name) VALUES (?)'
        cursor.execute(cmd, [group])
        self.connection.commit()

    def add_week(self, week):
        cursor = self.connection.cursor()
        cmd = 'INSERT INTO Week(name) VALUES (?)'
        cursor.execute(cmd, [week])
        self.connection.commit()

    def add_day(self, day):
        cursor = self.connection.cursor()
        cmd = 'INSERT INTO Days(name) VALUES (?)'
        cursor.execute(cmd, [day])
        self.connection.commit()

    def add_schedule(self, group, para, day, week, subject, subject_type, teacher, auditorium):
        cursor = self.connection.cursor()
        request = 'INSERT INTO Schedule(group_id, para, day_id, week_id, subject, subject_type, teacher, auditorium) '\
                  'VALUES ((SELECT id FROM Grups WHERE name = ?), ?, (SELECT id FROM Days WHERE name = ?), (SELECT id '\
                  'FROM Week WHERE name = ?), ?, ?, ?, ?)'
        data_tuple = ([group], [para], [day], [week], [subject], [subject_type], [teacher], [auditorium])
        cursor.execute(request, data_tuple)
        self.connection.commit()
