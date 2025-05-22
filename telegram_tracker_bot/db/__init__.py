"""
Добавляет модуль поддержки базы данных.

"""

from .database import (
    add_sleep_record,
    add_calories_record,
    add_workout_record,
    get_records_last_n_days,
    initialize_db,
)

__all__ = [
    'add_sleep_record',
    'add_calories_record',
    'add_workout_record',
    'get_records_last_n_days',
    'initialize_db',
]
