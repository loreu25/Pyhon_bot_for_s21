import os
import certifi
import telebot
from db import db
from telebot import types
import json
import time
import logging
import psycopg2

logging.basicConfig(level=logging.INFO)

ADMIN_IDS = [843057860]

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    TELEGRAM_BOT_TOKEN = config['TELEGRAM_BOT_TOKEN']

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN отсутствует или пустой!")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
print("Бот запущен")
current_category = None

def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        types.KeyboardButton(text="Внести Red flag"),
        types.KeyboardButton(text="Внести Green flag"),
        types.KeyboardButton(text="Найти peer`a")
    )
    return keyboard
@bot.message_handler(content_types=['text'])
def get_text_message(message):
    logging.info(f"Получено сообщение: {message.text} от {message.from_user.id}")
    keyboard = get_main_keyboard()
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
    else:
        bot.send_message(
            message.from_user.id,
            "Я вас не понял. Введите /start, чтобы открыть меню."
        )

def add_flag(message, category):
    try:
        nickname = message.text
        db.add_to_flags(nickname, category)
        bot.send_message(
            message.from_user.id,
            f"Ник '{nickname}' успешно добавлен в категорию '{category}'!"
        )
    except Exception as e:
        bot.send_message(
            message.from_user.id,
            f"Ошибка при добавлении в базу: {e}"
        )
    ask_for_more(message)

def find_category(message):
    try:
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
    except Exception as e:
        bot.send_message(
            message.from_user.id,
            f"Ошибка при поиске в базе: {e}"
        )
    ask_for_more(message)

def ask_for_more(message):
    bot.send_message(
        message.from_user.id,
        "Что-то еще?",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(commands=['view_db'])
def view_db(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "У вас нет доступа к этой команде.")
        return
    try:
        records = db.get_all_flags()
        if records:
            response = "\n".join(
                [f"ID: {row['id']}, Ник: {row['nickname']}, Категория: {row['category']}" for row in records]
            )
        else:
            response = "База данных пуста."
    except psycopg2.Error as db_error:
        logging.error(f"Ошибка базы данных: {db_error}")
        response = "Ошибка при подключении к базе данных."
    except Exception as e:
        logging.error(f"Неизвестная ошибка: {e}")
        response = "Произошла ошибка. Попробуйте позже."
    finally:
        bot.reply_to(message, response)

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"Ошибка в работе бота: {e}")
        time.sleep(5)