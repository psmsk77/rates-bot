"""Сервисная часть. Проведение запросов. Обработка исключений"""
bot_name = 'bot_rate_v.0.1'
import telebot
import time
from datetime import datetime, timedelta
import os
#Определяем операционную систему
path_os = ('' if os.name == 'nt' else '/home/user/bot_rate/')
#Запуск бота
admin_id = os.getenv('ADMIN_ID')
bot = telebot.TeleBot(os.getenv('BOT_RATES_TOKEN'))

def start_logging():
    """"Логирование старта"""
    start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    bot_start_report = (f"{start_time} {bot_name} started "
                        # f"in {'Testing_Mode' if testing_flag == True else 'Working_Mode'} "
                        f"in {os.name.upper()}! \U0001f680\n")
    with open(f"{path_os}bot_rate.log", "a", encoding="utf-8") as log_file:
        log_file.write(bot_start_report)
    bot.send_message(admin_id, bot_start_report), print(bot_start_report)


def exception_logging(error):
    """Логирование исключений"""
    exception_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    report = (f"{exception_time} {error}.\n\n")
    with open(f"{path_os}bot_rate.log", "a", encoding="utf-8") as log_file:
        log_file.write(report)


