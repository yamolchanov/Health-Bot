"""
ТЕСТ
"""
import os
import sqlite3
from datetime import datetime, timedelta
import pytest

from telegram_tracker_bot.db import (
    initialize_db,
    add_sleep_record,
    add_calories_record,
    add_workout_record,
    get_records_last_n_days
)

TEST_DB_NAME = "test_health_bot.db"


@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для создания тестовой БД и ее удаления после тестов"""
    if os.path.exists(TEST_DB_NAME):
        os.remove(TEST_DB_NAME)
    initialize_db(TEST_DB_NAME)
    yield
    if os.path.exists(TEST_DB_NAME):
        os.remove(TEST_DB_NAME)


def test_initialize_db(setup_database):
    """Тест инициализации базы данных"""

    conn = sqlite3.connect(TEST_DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_names = {table[0] for table in tables}
    assert 'sleep' in table_names
    assert 'calories' in table_names
    assert 'workouts' in table_names
    conn.close()


def test_add_sleep_record(setup_database):
    """Тест добавления записи о сне"""
    user_id = 1
    test_date = "2023-01-01"
    hours = 8.5
    add_sleep_record(user_id, test_date, hours, TEST_DB_NAME)
    conn = sqlite3.connect(TEST_DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sleep WHERE user_id = ?", (user_id,))
    records = cursor.fetchall()
    assert len(records) == 1
    assert records[0][2] == test_date
    assert records[0][3] == hours
    conn.close()


def test_add_calories_record(setup_database):
    """Тест добавления записи о калориях"""
    user_id = 1
    test_date = "2023-01-02"
    amount = 2000
    add_calories_record(user_id, test_date, amount, TEST_DB_NAME)
    conn = sqlite3.connect(TEST_DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM calories WHERE user_id = ?", (user_id,))
    records = cursor.fetchall()
    assert len(records) == 1
    assert records[0][2] == test_date
    assert records[0][3] == amount
    conn.close()


def test_add_workout_record(setup_database):
    """Тест добавления записи о тренировке"""
    user_id = 1
    test_date = "2023-01-03"
    duration = 1.5
    activity = "running"
    add_workout_record(user_id, test_date, duration, activity, TEST_DB_NAME)
    conn = sqlite3.connect(TEST_DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workouts WHERE user_id = ?", (user_id,))
    records = cursor.fetchall()
    assert len(records) == 1
    assert records[0][2] == test_date
    assert records[0][3] == duration
    assert records[0][4] == activity
    conn.close()


def test_get_records_last_n_days(setup_database):
    """Тест получения записей за последние N дней"""
    user_id = 2
    today = datetime.now().date()
    test_dates = [
        (today - timedelta(days=i)).strftime('%Y-%m-%d')
        for i in range(5)
    ]
    for i, date in enumerate(test_dates):
        add_sleep_record(user_id, date, 7 + i * 0.5, TEST_DB_NAME)
    records = get_records_last_n_days(user_id, "sleep", 3, TEST_DB_NAME)
    assert len(records) == 3
    assert records[0]['date'] == test_dates[0]
    assert records[1]['date'] == test_dates[1]
    assert records[2]['date'] == test_dates[2]
    with pytest.raises(ValueError):
        get_records_last_n_days(user_id, "nonexistent_table", 3, TEST_DB_NAME)


def test_multiple_users(setup_database):
    """Тест работы с несколькими пользователями"""
    user1 = 10
    user2 = 20
    test_date = "2023-01-10"
    add_sleep_record(user1, test_date, 8, TEST_DB_NAME)
    add_calories_record(user1, test_date, 2000, TEST_DB_NAME)
    add_sleep_record(user2, test_date, 7, TEST_DB_NAME)
    add_calories_record(user2, test_date, 2500, TEST_DB_NAME)
    conn = sqlite3.connect(TEST_DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sleep WHERE user_id = ?", (user1,))
    assert len(cursor.fetchall()) == 1
    cursor.execute("SELECT * FROM calories WHERE user_id = ?", (user1,))
    assert len(cursor.fetchall()) == 1
    cursor.execute("SELECT * FROM sleep WHERE user_id = ?", (user2,))
    assert len(cursor.fetchall()) == 1
    cursor.execute("SELECT * FROM calories WHERE user_id = ?", (user2,))
    assert len(cursor.fetchall()) == 1
    conn.close()
