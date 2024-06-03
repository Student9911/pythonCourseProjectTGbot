# Этот файл является точкой входа в приложение
import telebot
from telebot import types
import json
import os
import logging
from dbHandler import count_users, send_message_to_all_users, read_user, create_user, count_users, delete_user
from admin import isAdmin

import boto3
from botocore.exceptions import ClientError

ID_ADMINUS1 = int(os.getenv('IDADMIN'))
ID_ADMINUS2 = int(os.getenv('IDADMIN2'))


def send_to_all_confirm(message):
    # Проверяем, что пользователь не отменил операцию
    if message.text != "Отмена":
        # Отправляем сообщение всем пользователям
        send_message_to_all_users(message.text)
        bot.send_message(message.chat.id, "Сообщение успешно отправлено всем подписчикам.")
    else:
        bot.send_message(message.chat.id, "Рассылка отменена.")


# Функция для отправки сообщения администратору
def send_admin_message(message):
    # Отправляем сообщение администратору
    bot.send_message(ID_ADMINUS1, f"Сообщение от подписчика: {message.text}\n{message.chat.id}")
    admin_chat_id = os.getenv('IDADMIN2')
    # bot.send_message(ID_ADMINUS2, f"Сообщение от подписчика: {message.text}\n{message.chat.id}")
    bot.send_message(message.chat.id,
                     "Сообщение отправлено администратору\nожидайте обратной связи, если вы указали свой телефон")


token = os.getenv('BOT_TOKEN')  # Получаем токен бота из переменных среды
bot = telebot.TeleBot(token, threaded=False)  # Создаем экземпляр бота

def handler(event, context):
    print(event)
    body = json.loads(event['body'])  # Получаем тело запроса
    update = telebot.types.Update.de_json(body)  # Преобразуем тело запроса в объект Update
    bot.process_new_updates([update])  # Обрабатываем новые обновления

@bot.message_handler(commands=['message'])
def handle_admin_message(message):
    remove_keyboard = types.ReplyKeyboardRemove()  # Создаем клавиатуру для удаления
    bot.send_message(message.chat.id,
                     "Введите текст сообщения,\nне забудьте указать ваше имя \n и контактный телефон для обратной связи:",
                     reply_markup=remove_keyboard)  # Отправляем сообщение с удалением клавиатуры
    bot.register_next_step_handler(message, send_admin_message)  # Регистрируем следующий обработчик

@bot.message_handler(commands=['count'])
def handle_admin_message(message):
    if isAdmin(message.from_user.id):  # Проверяем, является ли пользователь администратором
        users_count = count_users()  # Получаем количество пользователей в базе данных
        bot.send_message(message.chat.id, f"Количество подписчиков: {users_count}")  # Отправляем сообщение с количеством пользователей
    else:
        bot.send_message(message.chat.id, "вы не админ")  # Отправляем сообщение о том, что пользователь не является администратором

@bot.message_handler(commands=['send_to_all'])
def send_to_all(message):
    if isAdmin(message.from_user.id):  # Проверяем, является ли пользователь администратором
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Создаем клавиатуру
        cancel_button = types.KeyboardButton('Отмена')  # Создаем кнопку "Отмена"
        keyboard.add(cancel_button)  # Добавляем кнопку на клавиатуру

        bot.send_message(message.chat.id, "Введите текст сообщения для рассылки:", reply_markup=keyboard)  # Запрашиваем у пользователя текст сообщения
        bot.register_next_step_handler(message, send_to_all_confirm)  # Регистрируем следующий обработчик
    else:
        bot.send_message(message.chat.id, "Вы не являетесь администратором.")  # Отправляем сообщение о том, что пользователь не является администратором

    # Обрабатываем команду /start


@bot.message_handler(commands=['start'])
def start_message(message):
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=os.environ.get('USER_STORAGE_URL'),
        region_name='us-east-1',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )
    # Создаем клавиатуру с кнопками "Подписаться" и "Отмена"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    subscribe_button = types.KeyboardButton('Подписаться')
    cancel_button = types.KeyboardButton('Отмена')
    keyboard.add(subscribe_button, cancel_button)

    # Проверяем, есть ли пользователь в базе
    user_query = read_user(message.chat.id, dynamodb)
    if not user_query:
        bot.send_message(message.chat.id, "Привет " + str(message.from_user.first_name))
        bot.send_message(message.chat.id,
                         'Хотите подписаться на нашего бота?\n' + 'ваш ID: ' + str(message.from_user.id),
                         reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id,
                         "Вы уже подписаны на новостную рассылку, " + str(message.from_user.first_name))


# Обрабатываем команду /price
@bot.message_handler(commands=['price'])
def price_message(message):
    price = 'Скоро админ добавит сюда актуальный прайс'
    bot.send_message(message.chat.id, price)


# Обрабатываем команду /mode
@bot.message_handler(commands=['mode'])
def mode_message(message):
    price = 'Скоро админ добавит сюда актуальный режим работы компании'
    bot.send_message(message.chat.id, price)


# Обрабатываем все сообщения
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text.lower() == "отписаться":
        response = delete_user(message.chat.id)
        # Убираем клавиатуру
        remove_keyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, response, reply_markup=remove_keyboard)
    elif message.text.lower() == "подписаться":
        response = create_user(message.chat.id, message.from_user.first_name)
        # Убираем клавиатуру
        remove_keyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, response, reply_markup=remove_keyboard)
    else:
        if isAdmin(message.from_user.id):
            if message.text != "назад":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                count_button = types.KeyboardButton('/count')
                send_to_all_button = types.KeyboardButton('/send_to_all')
                cancel_button = types.KeyboardButton('назад')
                markup.add(count_button, send_to_all_button, cancel_button)
                bot.send_message(message.chat.id, 'Выберите команду:', reply_markup=markup)
            else:
                remove_keyboard = types.ReplyKeyboardRemove()
                bot.send_message(message.chat.id, 'Отмена действий', reply_markup=remove_keyboard)


        else:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            cancel_button = types.KeyboardButton('Отписаться')
            keyboard.add(cancel_button)
            bot.send_message(message.chat.id,
                             "Привет, " + message.from_user.first_name + " я просто информационный бот, если вы больше не хотите получать рассылки, нажмите 'Отмена'",
                             reply_markup=keyboard)
