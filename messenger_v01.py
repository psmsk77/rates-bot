"""Рабочая программа (НЕ проверена на сервере)! ver.0.1"""
import telebot
from db_action import BotDB
import time
from datetime import datetime, timedelta
import os
import requests_rates
bot_name = 'bot_rate_messenger_v.0.1'
path_os = ('' if os.name=='nt' else '/home/user/bot_rate/')
admin_id = os.getenv('ADMIN_ID')
bot = telebot.TeleBot(os.getenv('BOT_RATES_TOKEN'))
timer_start = time.time()
BotDB = BotDB(f'{path_os}bot_rate.db')

#Запускаем бота. Запишем в лог время запуска бота.
def start():
    """Начало работы бота. Логгирование."""
    start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    bot_start_report = (f"{start_time} Bot {bot_name} started "
                        f"in {os.name.upper()}! \U0001f680\n")
    with open (f"{path_os}messenger.log","a", encoding="utf-8") as log_file:
        log_file.write(bot_start_report)
    bot.send_message(admin_id, bot_start_report)
    print(bot_start_report)

dict_rates = {}
def requests():
    """запрос данных, занесение данных в словарь"""
    #Запрос данных с алика
    dict_rates["aliexpress"] = requests_rates.ali()
    #Запрос данных у ЦБ
    dict_rates["cbr"] = requests_rates.exchange()
    #Запрос данных с Бинанс
    dict_rates["binance"] = requests_rates.crypto()
    return

def mailing():
    mailing_list = BotDB.create_mailing_list()
    print(mailing_list)
    message_counter = 0
    for i in range(len(mailing_list)):
        if mailing_list[i][1]==True:
            bot.send_message((mailing_list[i][0]), dict_rates["aliexpress"])
            #print(f'Отправил сообщение ID {mailing_list[i][0]}\n {dict_rates["aliexpress"]}')
            message_counter += 1
        if mailing_list[i][2]==True:
            bot.send_message((mailing_list[i][0]), dict_rates["cbr"])
            #print(f'Отправил сообщение ID {mailing_list[i][0]}\n {dict_rates["cbr"]}')
            message_counter += 1
        if mailing_list[i][3]==True:
            bot.send_message((mailing_list[i][0]), dict_rates["binance"])
            #print(f'Отправил сообщение ID {mailing_list[i][0]}\n {dict_rates["binance"]}')
            message_counter += 1
    return len(mailing_list), message_counter


#Запишем в лог время окончания работы бота
def finish():
    finish_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    timer_finish = time.time()
    #timer = round((timer_finish-timer_start), 0)
    timer = int(timer_finish-timer_start)
    bot_finish_report = (f"{finish_time} Bot {bot_name} finished! \U0001f3C1\n"
                         f"Пользователей в рассылке: {mail[0]}\n"
                         f"Отправлено сообщений: {mail[1]}\n"
                         f"Время рассылки составило: {timer} сек.\n")
    print(bot_finish_report)
    with open (f"{path_os}messenger.log","a", encoding="utf-8") as log_file:
        log_file.write(bot_finish_report)
    bot.send_message(admin_id, bot_finish_report)



if __name__ == "__main__":
    start()
    requests()
    mail = mailing()
    finish()