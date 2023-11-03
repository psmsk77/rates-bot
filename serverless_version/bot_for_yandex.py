"""Версия Telegram бота для Yandex Cloud Function (FaaS)"""
import telebot
from telebot import types
import os
import json

admin_id = os.getenv('CHAT_ID')  # Telegram ID
token = os.getenv('TG_TOKEN')  # Bot token
bot = telebot.TeleBot(token)  # Запуск бота


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
    return kb_main


def make_inline_keyboard(list):
    inline_btn_1 = types.InlineKeyboardButton(f'{"⬜" if list[0]==False else "✔"} Aliexpress', callback_data=f'{"btn1" if list[0]==False else "btn6"}')
    inline_btn_2 = types.InlineKeyboardButton(f'{"⬜" if list[1]==False else "✔"} Курсы ЦБ', callback_data=f'{"btn2" if list[1]==False else "btn7"}')
    inline_btn_3 = types.InlineKeyboardButton(f'{"⬜" if list[2]==False else "✔"} Крипта', callback_data=f'{"btn3" if list[2]==False else "btn8"}')
    inline_kb_full = types.InlineKeyboardMarkup(row_width=3).row(inline_btn_1, inline_btn_2, inline_btn_3)
    inline_kb_full.add(types.InlineKeyboardButton(f'✅ Подтвердить', callback_data='btn4'))
    inline_kb_full.add(types.InlineKeyboardButton(f'❌ Отказаться от рассылки', callback_data='btn5'))
    return inline_kb_full


def bot_edit_message_text(callback_chat_id, message_id, choice_list):
    """Функция редактирования сообщения бота bot.edit_message_text!"""
    bot.edit_message_text(f"Выберите категорию для рассылки, затем нажмите <b><i>Подтвердить</i></b>.\n"
                          f"Если вы хотите отказаться от рассылки, то нажмите <b><i>Отказаться от рассылки</i></b>.",
                          parse_mode='HTML', reply_markup=make_inline_keyboard(choice_list),
                          chat_id=callback_chat_id, message_id=message_id)


def process_callback(data, callback_query_id, callback_chat_id, message_id, choice_list):
    """Обработка запросов инлайн клавиатуры"""
    code = data[-1]
    if code.isdigit():
        code = int(code)
    if code == 1:
        bot.answer_callback_query(callback_query_id, text='Выбрана категория курс Aliexpress')
        # mailing_list[0]=True
        choice_list[0] = True
        bot_edit_message_text(callback_chat_id, message_id, choice_list)
    elif code == 2:
        bot.answer_callback_query(callback_query_id, text='Выбрана категория курсы ЦБ')
        # mailing_list[1] = True
        choice_list[1] = True
        bot_edit_message_text(callback_chat_id, message_id, choice_list)
    elif code == 3:
        bot.answer_callback_query(callback_query_id, text='Выбрана категория курсы криптовалют')
        choice_list[2] = True
        bot_edit_message_text(callback_chat_id, message_id, choice_list)
    elif code == 4:
        if choice_list[0] and choice_list[1] and choice_list[2] == False:
            response_text = "⚠ ОШИБКА!\n\nЧтобы подписаться на рассылку необходимо выбрать не менее одной категории."
            bot.answer_callback_query(callback_query_id, text=response_text, show_alert=True)
        else:
            response_text = "Вы успешно подписались на рассылку!"
            bot.answer_callback_query(callback_query_id, text=response_text, show_alert=True)
            bot.edit_message_reply_markup(callback_chat_id, message_id, reply_markup=None)
    elif code == 5:
        bot.answer_callback_query(callback_query_id, text='Вы успешно отказались от рассылки! Ждем Вас снова!', show_alert=True)
        bot.edit_message_reply_markup(callback_chat_id, message_id, reply_markup=None)
        # bot.delete_message(callback_query.message.chat.id, callback_query.message.id)  # Можно удалить клавиатуру так.

    elif code == 6:
        bot.answer_callback_query(callback_query_id, text='Отменена категория курс Aliexpress')
        choice_list[0] = False
        bot_edit_message_text(callback_chat_id, message_id, choice_list)
    elif code == 7:
        bot.answer_callback_query(callback_query_id, text='Отменена категория курсы ЦБ')
        choice_list[1] = False
        bot_edit_message_text(callback_chat_id, message_id, choice_list)
    elif code == 8:
        bot.answer_callback_query(callback_query_id, text='Отменена категория курсы криптовалют')
        choice_list[2] = False
        bot_edit_message_text(callback_chat_id, message_id, choice_list)
    else:
        bot.answer_callback_query(callback_query_id)


def start(chat_id, user_name, res=False):
    """Обработка команды start"""

    bot.send_message(chat_id, f"<b>Привет, {user_name}!</b> \U0001F44B\n\n"
                                      f"<b>Это Валютный Бот! Я сообщаю курсы валют.</b>\n\n"
                                      f"💲 Я знаю не только <b>курсы ЦБ</b> по доллару, евро и юаню, "
                                      f"но и курсы <b>криптовалют</b>.\n\n"
                                      f"\U000026A1 <b>А еще, я знаю курс доллара на Aliexpress!</b>\n"
                                      f"<i>Следи за курсом, чтобы сделать покупку по выгодным ценам.</i>\n\n"
                                      f"<i>📨 Чтобы настроить бесплатную ежедневную рассылку с курсами валют "
                                      f"нажми 'Настроить ежедневную рассылку'.</i>\n\n"
                                      f"\U00002B07 Какая валюта тебя интересует? \U00002B07",
                                        parse_mode='HTML', reply_markup=make_keyboard())


def help(chat_id, res=False):
    """Обработка команды help"""
    bot.send_message(chat_id, f'СПРАВКА\n\n '
                                      f'\U0000267B В случае возникновения ошибок "очистите историю чата" с ботом.\n\n'
                                      f'🖋 Для связи с разработчиками бота выберите пункт меню "Оставить отзыв" и отправьте ваше сообщение в чат.')


def mailing(chat_id, res=False):
    """Функция отправляет сообщение с инлайн клавиатурой"""
    choice_list = [False, False, False]
    bot.send_message(chat_id, f"Выберите категорию для рассылки, затем нажмите <b><i>Подтвердить</i></b>.\n"
                                      f"Если вы хотите отказаться от рассылки, то нажмите <b><i>Отказаться от рассылки</i></b>.",
                                        reply_markup=make_inline_keyboard(choice_list), parse_mode='HTML')


def handler(event, context):
    print(event)
    message_body = event['messages'][0]['details']['message']['body']
    res = json.loads(message_body)

    if 'callback_query' in res:
        callback_query_id = res['callback_query']['id']
        data = res['callback_query']['data']
        callback_chat_id = res['callback_query']['message']['chat']['id']
        message_id = res['callback_query']['message']['message_id']
        keyboard = res['callback_query']['message']['reply_markup']['inline_keyboard'][0]
        status1 = (False if keyboard[0]['callback_data'] == 'btn1' else True)
        status2 = (False if keyboard[1]['callback_data'] == 'btn2' else True)
        status3 = (False if keyboard[2]['callback_data'] == 'btn3' else True)
        choice_list = [status1, status2, status3]
        process_callback(data, callback_query_id, callback_chat_id, message_id, choice_list)
        return {
        'statusCode': 200,
        'body': 'Function completed successfully!',
        }

    chat_id = res['message']['chat']['id']
    user_name = res['message']['chat']['first_name']
    chat_text = res['message']['text']
    if chat_text == '/start':
        start(chat_id, user_name)
    elif chat_text == '/help':
        help(chat_id)
    elif chat_text == '🎁 Курс Aliexpress':
        bot.send_message(chat_id, "Функция в разработке")
    elif chat_text == '💰 Доллар, Евро, Юань':
        bot.send_message(chat_id, "Функция в разработке")
    elif chat_text == '🤑 Крипта':
        bot.send_message(chat_id, "Функция в разработке")
    elif chat_text == '⚙ Настроить ежедневную рассылку':
        mailing(chat_id)
    elif chat_text == '❓ Справка':
        help(chat_id)
    elif chat_text == '🖋 Оставить отзыв':
        bot.send_message(chat_id, "Функция в разработке")
        # bot.register_next_step_handler(message, get_feedback)
        # bot.send_message(message.chat.id, 'Отправьте ваши предложения о работе бота в чат.', reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(chat_id, chat_text)

    return {
        'statusCode': 200,
        'body': 'Function completed successfully!',
    }


# handler(None, None)
