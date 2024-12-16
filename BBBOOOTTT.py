import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
import os
import json
import re

# Токен для телеграм-бота
API_TOKEN = '8136774944:AAF9HhHax42vnA6ucdpCArAuuRtVyoP9BWs'

# Инициализация бота
bot = telebot.TeleBot(API_TOKEN)

DATA_PATH = 'habit_data.json'

# Главное меню
def main_menu():
    """Главное меню с кнопками"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add("Добавить привычку", "Список привычек")
    markup.add("Удалить привычку")
    markup.add("Вернуться")
    return markup

# Класс Habit для хранения привычек
class Habit:
    def __init__(self, name, goal, time_of_day):
        self.name = name
        self.goal = goal
        self.time_of_day = time_of_day
        self.completed = 0

# Класс для работы с привычками
class HabitTracker:
    def __init__(self):
        self.habits = []
        self.load_habits()

    def add_habit(self, habit):
        self.habits.append(habit)
        self.save_habits()

    def get_habits(self):
        return self.habits

    def remove_habit(self, name):
        self.habits = [habit for habit in self.habits if habit.name != name]
        self.save_habits()

    def save_habits(self):
        with open(DATA_PATH, 'w') as f:
            json.dump([habit.__dict__ for habit in self.habits], f)

    def load_habits(self):
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, 'r') as f:
                habits_data = json.load(f)
                for habit_data in habits_data:
                    habit = Habit(habit_data['name'], habit_data['goal'], habit_data['time_of_day'])
                    habit.completed = habit_data['completed']
                    self.habits.append(habit)

# Инициализация трекера привычек
tracker = HabitTracker()

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Привет! Я бот для формирования привычек!", reply_markup=main_menu())

# Обработчик кнопки "Добавить привычку"
@bot.message_handler(func=lambda message: message.text == "Добавить привычку")
def add_habit(message):
    bot.send_message(message.chat.id, "Введите название привычки:", reply_markup=main_menu())
    bot.register_next_step_handler(message, process_habit_name)

def process_habit_name(message):
    if message.text == "Вернуться":
        bot.send_message(message.chat.id, "🔙 Возвращаемся в главное меню.", reply_markup=main_menu())
        return
    name = message.text
    msg = bot.send_message(message.chat.id, "Введите количество дней для выполнения привычки:")
    bot.register_next_step_handler(msg, process_habit_goal, name)

def process_habit_goal(message, name):
    if message.text == "Вернуться":
        bot.send_message(message.chat.id, "🔙 Возвращаемся в главное меню.", reply_markup=main_menu())
        return
    try:
        goal = int(message.text)
        if goal <= 0:
            raise ValueError
        msg = bot.send_message(message.chat.id, "Введите время для напоминания (в формате ЧЧ:ММ):")
        bot.register_next_step_handler(msg, process_habit_time, name, goal)
    except ValueError:
        bot.send_message(message.chat.id, "⛔ Цель должна быть целым положительным числом. Попробуйте снова.")
        add_habit(message)

def process_habit_time(message, name, goal):
    if message.text == "Вернуться":
        bot.send_message(message.chat.id, "🔙 Возвращаемся в главное меню.", reply_markup=main_menu())
        return
    time_of_day = message.text
    if re.match(r'^[0-2][0-9]:[0-5][0-9]$', time_of_day):
        habit = Habit(name, goal, time_of_day)
        tracker.add_habit(habit)
        bot.send_message(message.chat.id, f"✅ Привычка '{name}' добавлена на {goal} дней в {time_of_day}!", reply_markup=main_menu())
    else:
        msg = bot.send_message(message.chat.id, "⛔ Неверный формат времени. Попробуйте снова (ЧЧ:ММ):")
        bot.register_next_step_handler(msg, process_habit_time, name, goal)

# Обработчик кнопки "Список привычек"
@bot.message_handler(func=lambda message: message.text == "Список привычек")
def list_habits(message):
    habits = tracker.get_habits()
    if habits:
        response = "📋 Ваши привычки:\n\n"
        for habit in habits:
            response += f"🔹 {habit.name} - Цель: {habit.goal} дней, Время: {habit.time_of_day}\n"
        bot.send_message(message.chat.id, response, reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "😔 У вас пока нет добавленных привычек.", reply_markup=main_menu())

# Обработчик кнопки "Удалить привычку"
@bot.message_handler(func=lambda message: message.text == "Удалить привычку")
def delete_habit(message):
    bot.send_message(message.chat.id, "Введите название привычки, которую хотите удалить:", reply_markup=main_menu())
    bot.register_next_step_handler(message, process_delete_habit)

def process_delete_habit(message):
    if message.text == "Вернуться":
        bot.send_message(message.chat.id, "🔙 Возвращаемся в главное меню.", reply_markup=main_menu())
        return
    name = message.text
    tracker.remove_habit(name)
    bot.send_message(message.chat.id, f"🗑 Привычка '{name}' удалена.", reply_markup=main_menu())

# Обработчик кнопки "Вернуться"
@bot.message_handler(func=lambda message: message.text == "Вернуться")
def return_to_menu(message):
    bot.send_message(message.chat.id, "🔙 Возвращаемся в главное меню.", reply_markup=main_menu())

# Запуск бота
bot.polling(none_stop=True)