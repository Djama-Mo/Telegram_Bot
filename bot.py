import os
import telebot
# from telebot import apihelper
from telebot import types
from telebot.types import Message
import requests
from bs4 import BeautifulSoup as bs

TOKEN = '1357603426:AAFrXorWSFTIsndM4pKLTSOXCeMKqx7HYGE'

PROXY = os.environ.get('PROXY')
# apihelper.proxy = {'https': 'socks5://telegram:telegram@qcpfo.tgproxy.me:1080'}
# apihelper.proxy = {'http': 'http://10.10.1.10:3128'}

bot = telebot.TeleBot(TOKEN)

text_help = 'Ты можешь выбрать одну из нижеперечисленных команд:\n\n' \
            "/start - Начнем?))\n" \
            '/weather - Показать погоду'

url = 'https://yandex.ru/pogoda/moscow'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 '
                  'Safari/537.36 OPR/68.0.3618.63'}

r = requests.get(url, headers=headers)

soup = bs(r.text, 'html.parser')

show_days = soup.find_all('div', {'class': 'forecast-briefly__day'})

result = []

for day in show_days:
    name = day.find('div', {'class': 'forecast-briefly__name'}).text
    date = day.find('time', {'class': 'time forecast-briefly__date'}).text

    try:
        day1 = day.find('div', {'class': 'temp forecast-briefly__temp forecast-briefly__temp_day'}).find('span', {
            'class': 'temp__pre-a11y a11y-hidden'}).text
    except AttributeError:
        day1 = day.find('div', {'class': 'temp forecast-briefly__temp forecast-briefly__temp_day'}).find('span', {
            'class': 'temp__pre'}).text
    value_day = day.find('div', {'class': 'temp forecast-briefly__temp forecast-briefly__temp_day'}).find('span', {
        'class': 'temp__value'}).text
    grad_day = day.find('div', {'class': 'temp forecast-briefly__temp forecast-briefly__temp_day'}).find('span', {
        'class': 'temp__unit i-font i-font_face_yandex-sans-text-medium'}).text

    try:
        night = day.find('div', {'class': 'temp forecast-briefly__temp forecast-briefly__temp_night'}).find('span', {
            'class': 'temp__pre-a11y a11y-hidden'}).text
    except AttributeError:
        night = day.find('div', {'class': 'temp forecast-briefly__temp forecast-briefly__temp_night'}).find('span', {
            'class': 'temp__pre'}).text
    value_night = day.find('div', {'class': 'temp forecast-briefly__temp forecast-briefly__temp_night'}).find('span', {
        'class': 'temp__value'}).text
    grad_night = day.find('div', {'class': 'temp forecast-briefly__temp forecast-briefly__temp_night'}).find('span', {
        'class': 'temp__unit i-font i-font_face_yandex-sans-text-medium'}).text
    condition = day.find('div', {'class': 'forecast-briefly__condition'}).text

    day = f'{name} {date}\n{day1} {value_day}{grad_day}\n{night} {value_night}{grad_night}\n{condition}'
    result.append(day)


with open('days.txt', 'w') as fh:
    for day in result:
        fh.write(f'{day}\n\n')


@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    bot.send_message(message.chat.id, 'Привет\nЯ покажу тебе погоду в Москве')


@bot.message_handler(commands=['help'])
def send_list(message: Message):
    bot.send_message(message.chat.id, text_help)


@bot.message_handler(commands=['weather'])
def send_weather(message):
    markup = types.ReplyKeyboardMarkup()
    itembtn1 = types.KeyboardButton('Сегодня')
    itembtn3 = types.KeyboardButton('На следующие 3 дня')
    itembtnweek = types.KeyboardButton('На неделю')
    itembtnall = types.KeyboardButton('На месяц')
    markup.row(itembtn1, itembtn3)
    markup.row(itembtnweek, itembtnall)
    bot.send_message(message.chat.id, "Выбери одно из ниже указанных:", reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def answers(message: Message):
    id_ = message.chat.id
    if message.text == 'Сегодня':
        bot.send_message(id_, result[4])
    elif message.text == 'На следующие 3 дня':
        bot.send_message(id_, f'{result[4]}\n\n{result[5]}\n\n{result[6]}')
    elif message.text == 'На неделю':
        bot.send_message(id_, f'{result[4]}\n\n{result[5]}\n\n{result[6]}\n\n{result[7]}\n\n{result[8]}'
                              f'\n\n{result[9]}\n\n{result[10]}')
    if message.text == 'На месяц':
        with open('days.txt', 'r') as fh:
            text = fh.read()
        bot.send_message(id_, text)


if __name__ == '__main__':
    bot.polling(none_stop=True)
