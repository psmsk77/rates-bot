# Версия Telegram бота для Yandex Cloud Function (FaaS)

Телеграм бот на Python, адаптированный для работы в Yandex Cloud Function.

### Для работы бота необходимо:

* Зарегистрировать бота
  * Напишите боту `@BotFather` команду `/newbot` и следуйте инструкциям
  * Сохраните полученный токен
* Создать аккаунт в Yandex Cloud
* Зайти в свой аккаунт Yandex Cloud и выполнить следующие действия:
  * Создать Message Queue
  * Создать API Gateway
  * Скопировать URL из Message Queue в спецификацию API Gateway
    * Пример заполнения спецификации находится в файле `specification.yaml`
  * Создать Cloud Function со средой выполнения не ниже Python 3.9
    * Скопировать код из репозитория в файл `index.py`
    * Создать файл `requirements.txt` и скопировать в него названия необходимых библиотек из файла в репозитории
    * Обязательно укажите переменные окружения `CHAT_ID` (ваш id) и `TG_TOKEN` (токен бота)
  * Создать триггер для Message Queue, который принимает сообщения из очереди и передает их в функцию для обработки
* Готово! Подключитесь к боту в Telegram и нажмите кнопку `START` или нажмите в меню `/start`

*_При необходимости добавьте свои функции._*