import requests
from bs4 import BeautifulSoup
import time
from lxml import etree
from datetime import datetime, timedelta
import random
import service
from db_action import BotDB
import os

path_os = ('' if os.name == 'nt' else '/home/user/bot_rate/') # Определяем операционную систему
BotDB=BotDB(f'{path_os}bot_rate.db') #Подключение к БД

def ali():
    """Запрос курса на Aliexpress"""
    url = ["https://aliexpress.ru/item/4000989870531.html?sku_id=10000013206512605",
           "https://aliexpress.ru/item/1005002324886891.html?sku_id=12000020094040029",
           "https://aliexpress.ru/item/4000939906574.html?sku_id=10000011334711491"]
    for i in range(3):
        try:
            response = requests.get(url[random.randrange(len(url))])
            if not response.ok:
                raise Exception(f"Connecting to Aliexpress. Error {response.status_code}")
            break
        except Exception as error:
            service.exception_logging(error)
            print(f"Ошибка {error}. Повторный запрос.")
            if i == 2:
                answer = "Временно недоступно. Повторите запрос позднее."
                return answer
            time.sleep(3)
    bs = BeautifulSoup(response.text, "lxml")
    #price = bs.find("div", class_="snow-price_SnowPrice__mainS__18x8np") #Перестала работать
    price = bs.find("div", class_="snow-price_SnowPrice__mainS__azqpin")
    price = price.text.strip().replace(",", ".")
    price = price[:price.find(" ")]
    BotDB.update_rate(price, "ALI")
    answer=(f"Актуальный курс 1 USD на Aliexpress {price} руб.")
    return answer


def exchange():
    """Запрос курсов ЦБ"""
    today_exchange = datetime.now().date().strftime('%d/%m/%Y')
    url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={today_exchange}"
    for i in range(3):
        try:
            response = requests.get(url)
            if not response.ok:
                raise Exception(f"Connecting to Central Bank. Error {response.status_code}")
            break
        except Exception as error:
            service.exception_logging(error)
            print(f"Ошибка {error}. Повторный запрос.")
            if i == 2:
                answer = "Временно недоступно. Повторите запрос позднее."
                return answer
            time.sleep(3)
    root = etree.fromstring(response.content)
    charcode = root.xpath("//Valute/CharCode/text()")
    #nominal = root.xpath("//Valute/Nominal/text()")
    value1 = root.xpath("//Valute/Value/text()")
    exchange_dict = {}
    for i in range(len(charcode)):
        exchange_dict[charcode[i]] = float(str(value1[i]).replace(',','.'))
    # Обновляем в БД
    BotDB.update_rate(exchange_dict["USD"], "USD")
    BotDB.update_rate(exchange_dict["EUR"], "EUR")
    BotDB.update_rate(exchange_dict["CNY"], "CNY")
    #Отправляем ответ
    answer = (f'Курсы валют ЦБ на сегодня:\n'
              f' \U0001F4B5 1 USD = {round(float(exchange_dict["USD"]), 2)} руб.\n'
              f' \U0001F4B6 1 EUR = {round(float(exchange_dict["EUR"]), 2)} руб.\n'
              f' \U0001F4B4 1 CNY = {round(float(exchange_dict["CNY"]), 2)} руб.\n')
    return answer

def crypto():
    """Запрос курсов Binance"""
    global dict, coins
    dict = {}
    coins = ['BTC', 'ETH', 'LTC', 'DOGE']
    response_text = ['Курсы криптовалют:\n']
    for i in range(len(coins)):
        url = f'https://api.binance.com/api/v3/trades?symbol={coins[i]}USDT'
        # Запрашиваем данные
        for x in range(3):
            try:
                response = requests.get(url, params={'limit': 1})
                if not response.ok:
                    raise Exception(f"Connecting to Binance. Error {response.status_code}")
                break
            except Exception as error:
                service.exception_logging(error)
                print(f"Ошибка {error}. Повторный запрос.")
                if i == 2:
                    answer = "Временно недоступно. Повторите запрос позднее."
                    return answer
                time.sleep(3)
        # Приводим данные в нормальный вид
        price = response.json()
        price = price[0]
        price = float(price['price'])
        price = response.json()
        price = price[0]
        price = float(price['price'])
        dict[coins[i]] = price
        response_text.append(f'1 {coins[i]} = $ {dict[coins[i]]}\n')
        # Обновим в БД
        BotDB.update_rate(price, coins[i])
    answer = (''.join(response_text) if len(response_text) > 1 else 'Ошибка. Повторите запрос позднее.')
    return answer