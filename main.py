import json
import telebot


def get_token(filename):
    with open(filename, 'r', encoding="utf-8") as file:
        json_file = json.load(file)
        return json_file['token']


bot = telebot.TeleBot(token=get_token('auth.json'))


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Здравствуйте")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()
