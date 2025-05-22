"""
Модуль для работы с базой данных SQLite для Telegram-бота
по отслеживанию здоровья пользователя.

Включает функции для:
- Инициализации базы данных и создания необходимых таблиц
  (сон, калории, тренировки)
- Добавления записей о сне, калориях и тренировках
- Получения записей за последние N дней для указанного пользователя

Используется база данных с именем, заданным в конфигурации
(переменная DATABASE_NAME).
"""


import sqlite3
import datetime
from typing import Union, Any


def initialize_db(database_dir: str) -> None:
    """
    Инициализирует базу данных и создает таблицы, если их нет.

    Args:
        database_dir (str): Директория базы данных
    """
    conn = sqlite3.connect(database_dir)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sleep (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            hours REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            amount INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            duration_hours REAL NOT NULL,
            activity_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


def add_sleep_record(user_id: int, date: str,
                     hours: float, database_dir: str) -> None:
    """
    Добавляет запись о сне.

    Args:
        database_dir (str) : Директория базы данных
        user_id (int): ID-пользователя
        date (str): Дата
        hours (float): Время
    """
    conn = sqlite3.connect(database_dir)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sleep (user_id, date, hours) VALUES (?, ?, ?)",
                   (user_id, date, hours))
    conn.commit()
    conn.close()


def add_calories_record(user_id: int, date: str,
                        amount: int, database_dir: str) -> None:
    """
    Добавляет запись о калориях.

    Args:
        database_dir (str): Директория базы данных
        user_id (int): ID-пользователя
        date (str): Дата
        amount (int): Количество калорий
    """
    conn = sqlite3.connect(database_dir)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO calories (user_id, date, amount) VALUES (?, ?, ?)",
        (user_id,
         date,
         amount))
    conn.commit()
    conn.close()


def add_workout_record(
        user_id: int,
        date: str,
        duration_hours: float,
        activity_type: str, database_name: str) -> None:
    """
Добавляет запись о тренировке.

Args:
    database_name (str): Директория базы данных
    user_id (int): ID пользователя.
    date (str): Дата тренировки в формате ГГГГ-ММ-ДД.
    duration_hours (float): Длительность тренировки в часах.
    activity_type (str): Тип активности.

"""
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO workouts (user_id, date, duration_hours, activity_type)"
        " VALUES (?, ?, ?, ?)",
        (user_id,
         date,
         duration_hours,
         activity_type))
    conn.commit()
    conn.close()


def get_records_last_n_days(user_id: int,
                            table_name: str, n_days: int, database_name: str)\
        -> list[Union[dict[Any, Any], dict[str, Any],
                dict[str, str], dict[bytes, bytes]]]:
    """
        Получает записи пользователя за последние N дней из указанной таблицы.

        Args:
            database_name (str): Директория базы данных
            user_id (int): ID пользователя.
            table_name (str): Название таблицы базы данных.
            n_days (int): Количество последних дней для выборки.

        Returns:
            list[Union[dict[Any, Any], dict[str, Any],
             dict[str, str], dict[bytes, bytes]]]:
                Список записей в виде словарей с
                 разными типами ключей и значений.

        Raises:
            ValueError: Если переданы некорректные параметры.
        """
    conn = sqlite3.connect(database_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=n_days - 1)
    start_date_str = start_date.strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')
    if table_name not in ["sleep", "calories", "workouts"]:
        raise ValueError("Invalid table name")
    query = (f"SELECT * FROM {table_name}"
             " WHERE user_id = ? AND date >= ? "
             "AND date <= ? ORDER BY date DESC")
    cursor.execute(query, (user_id, start_date_str, today_str))
    records = cursor.fetchall()
    conn.close()
    return [dict(row) for row in records]
