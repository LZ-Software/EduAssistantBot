import json
import telebot

from telebot import types
from threading import Thread

from db import DB
from downloader import Downloader
from html_parser import HTMLParser
from xlsx_parser import XLSXParser
from log import Logger


def get_token(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        json_file = json.load(file)
        return json_file['token']


def get_schedule():
    hp = HTMLParser()
    hp.get_html()
    files = hp.parse_html()
    Downloader.download_files(files)
    for file in files.keys():
        xp = XLSXParser(file)
        xp.parse_file()


db = DB()
bot = telebot.TeleBot(token=get_token('auth.json'))


def start_bot():
    Logger.ok('БОТ ЗАПУЩЕН')
    bot.infinity_polling()


def get_authorized_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    schedule_button = types.KeyboardButton('Расписание')
    help_button = types.KeyboardButton('Список команд')
    delete_button = types.KeyboardButton('Отписаться от группы')
    markup.add(schedule_button, help_button)
    markup.add(delete_button)
    return markup


def get_no_markup():
    markup = types.ReplyKeyboardRemove()
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if db.get_user(user_id) is None:
        bot.send_message(message.chat.id,
                         text='Введите группу в формате <b><i>АААА-00-00</i></b>',
                         parse_mode='html')
    else:
        bot.send_message(message.chat.id,
                         text='Подписан на группу',
                         reply_markup=get_authorized_markup())


@bot.message_handler(regexp='([А-Я][А-Я][А-Я][А-Я]-[0-9][0-9]-[0-9][0-9])')
def set_group(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    flag, group_id = db.get_group_id(message.text)
    if flag:
        if db.add_user(user_id, name):
            if db.subscribe_user(user_id, group_id):
                bot.send_message(message.chat.id,
                                 text='Авторизация успешна',
                                 reply_markup=get_authorized_markup())
            else:
                bot.send_message(message.chat.id,
                                 text='Не удалось подписаться на группу',
                                 reply_markup=get_no_markup())
        else:
            bot.send_message(message.chat.id,
                             text='Не удалось добавить пользователя в базу',
                             reply_markup=get_no_markup())
    else:
        bot.send_message(message.chat.id,
                         text='Такая группа не найдена',
                         reply_markup=get_no_markup())


@bot.message_handler(content_types=['text'])
def func(message):
    user_id = message.from_user.id
    if message.text == 'Расписание':  # TODO: ВЫВОД РАСПИСАНИЯ
        pass
    elif message.text == 'Отписаться от группы':
        db.unsubscribe_user(user_id)
        bot.send_message(message.chat.id,
                         text='Вы успешно отвязаны от группы')
        bot.send_message(message.chat.id,
                         text='Введите группу в формате <b><i>АААА-00-00</i></b>',
                         reply_markup=get_no_markup(),
                         parse_mode='html')
    else:  # TODO: ОБРАБОТКА ОСТАЛЬНЫХ КНОПОК
        bot.send_message(message.chat.id,
                         text='Сделайте то, о чем вас просят',
                         reply_markup=get_no_markup())


if db.has_records():
    start_bot()
else:
    th = Thread(target=get_schedule())
    th.start()
    th.join()
    start_bot()
