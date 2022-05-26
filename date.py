import calendar
import datetime
import locale
import sys


class Date:

    __start_week_id = datetime.date(2022, 2, 9).isocalendar().week

    @staticmethod
    def get_week_of_the_year_number():
        current_week_id = datetime.date.today().isocalendar().week
        return current_week_id

    @staticmethod
    def get_study_week_number():
        week_number = Date.get_week_of_the_year_number() - Date.__start_week_id + 1
        return week_number

    @staticmethod
    def get_day_number():
        current_day_id = datetime.date.today().weekday() + 1
        return current_day_id

    @staticmethod
    def get_today():
        today = datetime.date.today()
        return today

    @staticmethod
    def get_next_monday():
        today = datetime.date.today()
        next_monday = today + datetime.timedelta(days=-today.weekday(), weeks=1)
        return next_monday

    @staticmethod
    def get_parity():
        if Date.get_study_week_number() % 2 == 0:
            return 0
        else:
            return 1

    @staticmethod
    def get_current_date_str(shift):
        if shift == 0:
            day = datetime.date.today()
        else:
            day = datetime.date.today() + datetime.timedelta(days=shift)
        if sys.platform == 'win32':
            locale.setlocale(locale.LC_ALL, 'rus_rus')
        else:
            locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        day_format = day.strftime('%d %b %Y')
        return day_format

    @staticmethod
    def get_weekday_name_str(shift):
        if shift == 0:
            day = datetime.date.today()
        else:
            day = datetime.date.today() + datetime.timedelta(days=shift)
        if sys.platform == 'win32':
            locale.setlocale(locale.LC_ALL, 'rus_rus')
        else:
            locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        day_name = calendar.day_name[day.weekday()].title()
        return day_name

    @staticmethod
    def get_formatted_date_title(day=0, week=0):
        formatted_date = f'<b>[Неделя {Date.get_study_week_number()+week}]\n{Date.get_weekday_name_str(day)}, ' \
                         f'{Date.get_current_date_str(day)}</b>\n\n'
        return formatted_date
