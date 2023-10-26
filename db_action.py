"""Здесь происходит обработка команд с базой данных SQLite"""
import sqlite3
from datetime import datetime


class BotDB:
    def __init__(self, db_file):
        """"Инициализация соединения с БД"""
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def user_exist(self, chat_id):
        """Проверяем, есть ли юзер в БД"""
        result = self.cursor.execute("SELECT chat_id FROM bot_users WHERE chat_id = ?", (chat_id,))
        return bool(len(result.fetchall()))

    def add_user(self, chat_id, username, first_name, last_name):
        """Добавляем юзера в БД"""
        self.cursor.execute("INSERT INTO bot_users (chat_id, username, first_name, last_name) "
                            "VALUES (?, ?, ?, ?)", (chat_id, username, first_name, last_name,))
        return self.conn.commit()

    def add_action(self, chat_id, action):
        """Добавляем информацию о действии юзера в БД"""
        self.cursor.execute("INSERT INTO user_actions (chat_id, user_action) VALUES (?, ?)", (chat_id, action,))
        return self.conn.commit()

    def add_to_mailing_list(self, chat_id, list):
        """Проверяем, есть ли юзер в таблице подписок. Добавляем юзера в рассылку"""
        result = self.cursor.execute("SELECT chat_id FROM subscription WHERE chat_id = ?", (chat_id,))
        if not bool(len(result.fetchall())):
            self.cursor.execute("INSERT INTO subscription (chat_id) VALUES (?)", (chat_id,))
            self.conn.commit()
        self.cursor.execute("UPDATE subscription SET aliexpress=?, cbr=?, crypto=? WHERE chat_id=?",
                            (list[0], list[1], list[2], chat_id,))
        return self.conn.commit()

    def unsubscribe(self, chat_id):
        """Удаляем юзера из рассылки"""
        self.cursor.execute("DELETE FROM subscription WHERE chat_id=?", (chat_id,))
        return self.conn.commit()

    def create_mailing_list(self):
        """Получение списка пользователей для ежедневной рассылки"""
        result = self.cursor.execute("SELECT * FROM subscription;").fetchall()
        return result

    def request_rate(self, currency):
        """Запрашиваем курсы валют в БД"""
        result = self.cursor.execute("SELECT date, rate FROM rates WHERE currency = ?", (currency,))
        return result.fetchone()

    def update_rate(self, rate, currency):
        """Обновляем курсы валют в БД"""
        date = str(datetime.now())[:16]
        self.cursor.execute("UPDATE rates SET date=?, rate=? WHERE currency=?", (date, rate, currency,))
        return self.conn.commit()

    def close(self):
        """Закрытие соединения с БД"""
        self.connect.close()
