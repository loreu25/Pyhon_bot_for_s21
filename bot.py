import os
import certifi

# Установить корректный путь к сертификатам
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

import telebot
from db import db
from telebot import types
bot = telebot.TeleBot('7491331608:AAH5aqRaIRfJfdloIH2JyBqeH2cLiH2E2XQ')

current_category = None

@bot.message_handler(content_types=['text'])
def get_text_message(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    key_add_red = types.KeyboardButton(text="Внести Red flag")
    key_add_green = types.KeyboardButton(text="Внести Green flag")
    keyboard.add(key_add_red, key_add_green)
    key_find_peer = types.KeyboardButton(text="Найти peer`a")
    keyboard.add(key_find_peer)
    if message.text == "/start":
        bot.send_message(
            message.from_user.id,
            "Выберите действие:",
            reply_markup=keyboard
        )
    elif message.text == "Внести Red flag":
        bot.send_message(
            message.from_user.id,
            "Введите ник для добавления в Red flag:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, add_flag, "Red Flag")
    elif message.text == "Внести Green flag":
        bot.send_message(
            message.from_user.id,
            "Введите ник для добавления в Green flag:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, add_flag, "Green Flag")
    elif message.text == "Найти peer`a":
        bot.send_message(
            message.from_user.id,
            "Введите ник для нахождения peer`a:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, find_category)

def add_flag(message, category):
    nickname = message.text
    db.add_to_flags(nickname, category)
    bot.send_message(
        message.from_user.id,
        f"Ник '{nickname}' успешно добавлен в категорию '{category}'!"
    )
    ask_for_more(message)

def find_category(message):
    nickname = message.text
    category = db.find_peer(nickname)
    if category:
        bot.send_message(
            message.from_user.id,
            f"Ник '{nickname}' принадлежит к категории: {category}."
        )
    else:
        bot.send_message(
            message.from_user.id,
             f"Пользователь с ником '{nickname}' не найден в базе."
        )
    ask_for_more(message)

def ask_for_more(message):
    # Вопрос "Что-то еще?" и возврат клавиатуры
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    key_add_red = types.KeyboardButton(text="Внести Red flag")
    key_add_green = types.KeyboardButton(text="Внести Green flag")
    keyboard.add(key_add_red, key_add_green)
    key_find_peer = types.KeyboardButton(text="Найти peer`a")
    keyboard.add(key_find_peer)

    bot.send_message(
        message.from_user.id,
        "Что-то еще?",
        reply_markup=keyboard
    )


bot.polling(none_stop=True)
