"""Бот определяющий курсы валют. Версия 0.1"""
import telebot
from telebot import types
import time
from datetime import datetime, timedelta
import os
from db_action import BotDB
import service
import requests_rates


admin_id = os.getenv('ADMIN_ID')  # Telegram ID
token = os.getenv('BOT_RATES_TOKEN')  # Bot token
bot = telebot.TeleBot(os.getenv('BOT_RATES_TOKEN'))  # Запуск бота

path_os = ('' if os.name == 'nt' else '/home/user/bot_rate/')  # Определяем операционную систему
BotDB = BotDB(f'{path_os}bot_rate.db')  # Подключение к БД
# mailing_list=[False, False, False]


def make_keyboard():
    """Создание клавиатуры"""
    button1 = types.KeyboardButton('🎁 Курс Aliexpress')
    button2 = types.KeyboardButton('💰 Доллар, Евро, Юань')
    button3 = types.KeyboardButton('🤑 Крипта')
    button4 = types.KeyboardButton('⚙ Настроить ежедневную рассылку')
    button5 = types.KeyboardButton('❓ Справка')
    button6 = types.KeyboardButton('🖋 Оставить отзыв')
    global kb_main
    kb_main = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False).row(button1, button2, button3)
    kb_main = kb_main.add(button4)
    kb_main = kb_main.add(button5, button6)


def make_inline_keyboard(list):
    inline_btn_1 = types.InlineKeyboardButton(f'{"⬜" if list[0]==False else "✔"} Aliexpress', callback_data=f'{"btn1" if list[0]==False else "btn6"}')
    inline_btn_2 = types.InlineKeyboardButton(f'{"⬜" if list[1]==False else "✔"} Курсы ЦБ', callback_data=f'{"btn2" if list[1]==False else "btn7"}')
    inline_btn_3 = types.InlineKeyboardButton(f'{"⬜" if list[2]==False else "✔"} Крипта', callback_data=f'{"btn3" if list[2]==False else "btn8"}')
    inline_kb_full = types.InlineKeyboardMarkup(row_width=3).row(inline_btn_1, inline_btn_2, inline_btn_3)
    inline_kb_full.add(types.InlineKeyboardButton(f'✅ Подтвердить', callback_data='btn4'))
    inline_kb_full.add(types.InlineKeyboardButton(f'❌ Отказаться от рассылки', callback_data='btn5'))
    return inline_kb_full


def bot_edit_message_text(callback_query):
    """Функция редактирования сообщения бота bot.edit_message_text!"""
    bot.edit_message_text(f"Выберите категорию для рассылки, затем нажмите <b><i>Подтвердить</i></b>.\n"
                          f"Если вы хотите отказаться от рассылки, то нажмите <b><i>Отказаться от рассылки</i></b>.",
                          parse_mode='HTML', reply_markup=make_inline_keyboard(globals()[f'kb_{callback_query.message.chat.id}']),
                          chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)


@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith('btn'))
def process_callback(callback_query: types.CallbackQuery):
    """Обработка запросов инлайн клавиатуры"""
    code = callback_query.data[-1]
    if code.isdigit():
        code = int(code)
    if code == 1:
        bot.answer_callback_query(callback_query.id, text='Выбрана категория курс Aliexpress')
        # mailing_list[0]=True
        globals()[f'kb_{callback_query.message.chat.id}'][0] = True
        bot_edit_message_text(callback_query)
    elif code == 2:
        bot.answer_callback_query(callback_query.id, text='Выбрана категория курсы ЦБ')
        # mailing_list[1] = True
        globals()[f'kb_{callback_query.message.chat.id}'][1] = True
        bot_edit_message_text(callback_query)
    elif code == 3:
        bot.answer_callback_query(callback_query.id, text='Выбрана категория курсы криптовалют')
        # mailing_list[2] = True
        globals()[f'kb_{callback_query.message.chat.id}'][2] = True
        bot_edit_message_text(callback_query)
    elif code == 4:
        if globals()[f'kb_{callback_query.message.chat.id}'][0] == globals()[f'kb_{callback_query.message.chat.id}'][1] == globals()[f'kb_{callback_query.message.chat.id}'][2] == False:
            response_text = "⚠ ОШИБКА!\n\nЧтобы подписаться на рассылку необходимо выбрать не менее одной категории."
            bot.answer_callback_query(callback_query.id, text=response_text, show_alert=True)
        else:
            BotDB.add_to_mailing_list(callback_query.message.chat.id, globals()[f'kb_{callback_query.message.chat.id}'])
            response_text = "Вы успешно подписались на рассылку!"
            bot.answer_callback_query(callback_query.id, text=response_text, show_alert=True)
            bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.id, reply_markup=None)
    elif code == 5:
        bot.answer_callback_query(callback_query.id, text='Вы успешно отказались от рассылки! Ждем Вас снова!', show_alert=True)
        bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.id, reply_markup=None)
        # bot.delete_message(callback_query.message.chat.id, callback_query.message.id)  # Можно удалить клавиатуру так.
        BotDB.add_action(callback_query.message.chat.id, "unsubscribed")  # Добавляем инфо в таблицу действий пользователя
        BotDB.unsubscribe(callback_query.message.chat.id)
    elif code == 6:
        bot.answer_callback_query(callback_query.id, text='Отменена категория курс Aliexpress')
        globals()[f'kb_{callback_query.message.chat.id}'][0] = False
        bot_edit_message_text(callback_query)
    elif code == 7:
        bot.answer_callback_query(callback_query.id, text='Отменена категория курсы ЦБ')
        globals()[f'kb_{callback_query.message.chat.id}'][1] = False
        bot_edit_message_text(callback_query)
    elif code == 8:
        bot.answer_callback_query(callback_query.id, text='Отменена категория курсы криптовалют')
        globals()[f'kb_{callback_query.message.chat.id}'][2] = False
        bot_edit_message_text(callback_query)
    else:
        bot.answer_callback_query(callback_query.id)


@bot.message_handler(commands=["start"])
def start(message, res=False):
    """Обработка команды start"""
    print(message.chat)  # Сообщение от пользователя, который нажал /start

    bot.send_message(message.chat.id, f"<b>Привет, {message.chat.first_name}!</b> \U0001F44B\n\n"
                                      f"<b>Это Валютный Бот! Я сообщаю курсы валют.</b>\n\n"
                                      f"💲 Я знаю не только <b>курсы ЦБ</b> по доллару, евро и юаню, "
                                      f"но и курсы <b>криптовалют</b>.\n\n"
                                      f"\U000026A1 <b>А еще, я знаю курс доллара на Aliexpress!</b>\n"
                                      f"<i>Следи за курсом, чтобы сделать покупку по выгодным ценам.</i>\n\n"
                                      f"<i>📨 Чтобы настроить бесплатную ежедневную рассылку с курсами валют "
                                      f"нажми 'Настроить ежедневную рассылку'.</i>\n\n"
                                      f"\U00002B07 Какая валюта тебя интересует? \U00002B07",
                                        parse_mode='HTML', reply_markup=kb_main)

    # Проверим, есть ли ID пользователя в БД
    if not BotDB.user_exist(message.chat.id):  # Добавим юзера
        BotDB.add_user(message.chat.id, message.chat.username, message.chat.first_name, message.chat.last_name)
        BotDB.add_action(message.chat.id, "start")
        bot.send_message(admin_id, f"A new user has been registered\n"
                                        f"ID: {message.chat.id}\n"
                                        f"Name: {message.chat.first_name} {message.chat.last_name}\n")
        print('Добавлен новый пользователь!')
    else:  # Обновим
        BotDB.add_action(message.chat.id, "start")
        print("Пользователь уже существует! Обновим дату последнего входа.")


@bot.message_handler(commands=["aliexpress"])
def ali(message, res=False):
    """Обработка команды aliexpress"""
    BotDB.add_action(message.chat.id, "aliexpress")
    bot.send_message(message.chat.id, '\U0001F559 Выполняю...')
    # Проверяем дату обновления курса
    ali = BotDB.request_rate("ALI")
    if ali[0][:16] > str(datetime.now()-timedelta(minutes=10))[:16]:
        answer = (f"Актуальный курс 1 USD на Aliexpress {ali[1]} руб.")
    else:  # Запускаем обновление
        answer = requests_rates.ali()
    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=["exchange"])
def exchange(message, res=False):
    """Обработка команды exchange. Запрос курсов ЦБ"""
    BotDB.add_action(message.chat.id, "centralbank")
    bot.send_message(message.chat.id, '\U0001F559 Выполняю...')
    # Проверяем дату обновления курса
    usd = BotDB.request_rate("USD")
    if usd[0][:10] == str(datetime.now().date()):
        eur = BotDB.request_rate("EUR")
        cny = BotDB.request_rate("CNY")
        dict = {"USD": usd[1], "EUR": eur[1], "CNY": cny[1]}
        answer = (f'Курсы валют ЦБ на сегодня:\n'
                  f' \U0001F4B5 1 USD = {round(float(dict["USD"]), 2)} руб.\n'
                  f' \U0001F4B6 1 EUR = {round(float(dict["EUR"]), 2)} руб.\n'
                  f' \U0001F4B4 1 CNY = {round(float(dict["CNY"]), 2)} руб.\n')
    else:  # Запускаем обновление
        answer = requests_rates.exchange()
    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=["crypto"])
def crypto(message, res=False):
    """Обработка команды crypto"""
    BotDB.add_action(message.chat.id, "crypto")
    bot.send_message(message.chat.id, '\U0001F559 Выполняю...')
    # Проверяем дату обновления курса
    btc = BotDB.request_rate("BTC")
    if btc[0][:16] > str(datetime.now()-timedelta(minutes=5))[:16]:
        eth = BotDB.request_rate("ETH")
        ltc = BotDB.request_rate("LTC")
        doge = BotDB.request_rate("DOGE")
        dict = {"BTC": btc[1], "ETH": eth[1], "LTC": ltc[1], "DOGE": doge[1]}
        answer = (f"Курсы криптовалют:\n"
                  f"1 BTC  = $ {dict['BTC']}\n"
                  f"1 ETH  = $ {dict['ETH']}\n"
                  f"1 LTC  = $ {dict['LTC']}\n"
                  f"1 DOGE = $ {dict['DOGE']}")
    else:  # Запускаем обновление
        answer = requests_rates.crypto()
    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=["mailing"])
def mailing(message, res=False):
    """Функция отправляет сообщение с инлайн клавиатурой"""
    BotDB.add_action(message.chat.id, "subscribed")
    globals()[f'kb_{message.chat.id}'] = [False, False, False]
    bot.send_message(message.chat.id, f"Выберите категорию для рассылки, затем нажмите <b><i>Подтвердить</i></b>.\n"
                                      f"Если вы хотите отказаться от рассылки, то нажмите <b><i>Отказаться от рассылки</i></b>.",
                                        reply_markup=make_inline_keyboard(globals()[f'kb_{message.chat.id}']), parse_mode='HTML')
    # bot.send_message(message.chat.id, "Выберите категорию для рассылки: ", reply_markup=make_inline_keyboard(mailing_list))


@bot.message_handler(commands=["help"])
def help(message, res=False):
    """Обработка команды help"""
    BotDB.add_action(message.chat.id, "help")
    bot.send_message(message.chat.id, f'СПРАВКА\n\n '
                                      f'\U0000267B В случае возникновения ошибок "очистите историю чата" с ботом.\n\n'
                                      f'🖋 Для связи с разработчиками бота выберите пункт меню "Оставить отзыв" и отправьте ваше сообщение в чат.')


@bot.message_handler(commands=["feedback"])
def get_feedback(message):  # получаем сообщение с фидбэком
    """Обработка команды feedback"""
    BotDB.add_action(message.chat.id, "feedback")
    feedback_text = message.text
    with open(f"{path_os}feedback.txt", "a", encoding='utf8') as feedback_file:
        feedback_file.write(f'ID:{message.chat.id}\n Date: {datetime.now()}\n Feedback:{feedback_text}\n\n ')
    bot.send_message(message.chat.id, 'Благодарим, за обратную связь.', reply_markup=kb_main)
    bot.send_message(admin_id, f"You have a new feedback from\n"
                                 f"ID: {message.chat.id}\n"
                                 f"Name: {message.chat.first_name} {message.chat.last_name}\n"
                                 f"Text: {message.text}")


@bot.message_handler(content_types=["text"])
def handle_text(message):
    """Обработка текстовых сообщений. Вызов функций."""
    if message.text == '🎁 Курс Aliexpress':
        ali(message)
    elif message.text == '💰 Доллар, Евро, Юань':
        exchange(message)
    elif message.text == '🤑 Крипта':
        crypto(message)
    elif message.text == '⚙ Настроить ежедневную рассылку':
        mailing(message)
    elif message.text.strip() == '❓ Справка':
        help(message)
    elif message.text.strip() == '🖋 Оставить отзыв':
        bot.register_next_step_handler(message, get_feedback)
        bot.send_message(message.chat.id, 'Отправьте ваши предложения о работе бота в чат.', reply_markup=types.ReplyKeyboardRemove())


if __name__ == '__main__':
    make_keyboard()
    service.start_logging()
    # Запуск бота
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as error:
            service.exception_logging(error)
            print(error)
            time.sleep(10)
