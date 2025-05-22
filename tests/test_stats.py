from unittest.mock import patch
from telegram_tracker_bot.logic.stats import (
    format_timedelta,
    get_weekly_stats_text,
    get_data_for_advice
)
import telegram_tracker_bot.handlers

MOCK_SLEEP_DATA = [
    {'date': '2024-05-15', 'hours': 7.5},
    {'date': '2024-05-16', 'hours': 8.0},
    {'date': '2024-05-17', 'hours': 6.5},
    {'date': '2024-05-18', 'hours': 7.0},
    {'date': '2024-05-19', 'hours': 8.2},
    {'date': '2024-05-20', 'hours': 7.8},
    {'date': '2024-05-21', 'hours': 6.0},
]

MOCK_CALORIES_DATA = [
    {'date': '2024-05-15', 'amount': 2200},
    {'date': '2024-05-16', 'amount': 2500},
    {'date': '2024-05-17', 'amount': 2000},
    {'date': '2024-05-18', 'amount': 2300},
    {'date': '2024-05-19', 'amount': 2100},
    {'date': '2024-05-20', 'amount': 2400},
    {'date': '2024-05-21', 'amount': 1900},
]

MOCK_WORKOUTS_DATA = [
    {'date': '2024-05-16', 'activity_type': 'Running', 'duration_hours': 1.0},
    {'date': '2024-05-18', 'activity_type': 'Weightlifting', 'duration_hours': 1.5},
    {'date': '2024-05-19', 'activity_type': 'Running', 'duration_hours': 0.75},
    {'date': '2024-05-20', 'activity_type': 'Yoga', 'duration_hours': 0.5},
]


def test_format_timedelta():
    assert format_timedelta(7.5) == "07:30"
    assert format_timedelta(0.5) == "00:30"
    assert format_timedelta(10.0) == "10:00"
    assert format_timedelta(0.0) == "00:00"
    assert format_timedelta(24.0) == "24:00"
    assert format_timedelta(1.75) == "01:45"
@patch('telegram_tracker_bot.logic.stats.get_records_last_n_days')
def test_get_weekly_stats_text_with_data(mock_get_records):
    mock_get_records.side_effect = [
        MOCK_SLEEP_DATA,
        MOCK_CALORIES_DATA,
        MOCK_WORKOUTS_DATA
    ]
    user_id = 123
    report = get_weekly_stats_text(user_id)

    assert "📊 Статистика за последние 7 дней:" in report
    assert "😴 Сон:" in report
    assert "  - В среднем: 07:17 / ночь" in report
    assert "🍎 Калории:" in report
    assert "  - В среднем: 2200 ккал / день" in report
    assert "💪 Тренировки:" in report
    assert "  - Всего часов: 03:45" in report
    assert "  - По активностям:" in report
    assert "    - Weightlifting: 01:30" in report
    assert "    - Running: 01:45" in report
    assert "    - Yoga: 00:30" in report
    mock_get_records.assert_any_call(user_id, "sleep", 7, 'telegram_tracker_bot/db/tracker_data_base.db')
    mock_get_records.assert_any_call(user_id, "calories", 7, 'telegram_tracker_bot/db/tracker_data_base.db')
    mock_get_records.assert_any_call(user_id, "workouts", 7, 'telegram_tracker_bot/db/tracker_data_base.db')


@patch('telegram_tracker_bot.logic.stats.get_records_last_n_days')
def test_get_weekly_stats_text_no_data(mock_get_records):
    mock_get_records.side_effect = [[], [], []]
    user_id = 456
    report = get_weekly_stats_text(user_id)

    assert "😴 Сон: Нет данных за последние 7 дней." in report
    assert "🍎 Калории: Нет данных за последние 7 дней." in report
    assert "💪 Тренировки: Нет данных за последние 7 дней." in report


@patch('telegram_tracker_bot.logic.stats.get_records_last_n_days')
def test_get_data_for_advice_with_data(mock_get_records):
    mock_get_records.side_effect = [
        MOCK_SLEEP_DATA,
        MOCK_CALORIES_DATA,
        MOCK_WORKOUTS_DATA
    ]
    user_id = 789
    data = get_data_for_advice(user_id)
    _ = telegram_tracker_bot.handlers
    expected_sleep = [
        ('2024-05-15', 7.5), ('2024-05-16', 8.0), ('2024-05-17', 6.5),
        ('2024-05-18', 7.0), ('2024-05-19', 8.2), ('2024-05-20', 7.8),
        ('2024-05-21', 6.0)
    ]
    expected_calories = [
        ('2024-05-15', 2200), ('2024-05-16', 2500), ('2024-05-17', 2000),
        ('2024-05-18', 2300), ('2024-05-19', 2100), ('2024-05-20', 2400),
        ('2024-05-21', 1900)
    ]
    expected_workouts = [
        ('2024-05-16', 'Running', 1.0),
        ('2024-05-18', 'Weightlifting', 1.5),
        ('2024-05-19', 'Running', 0.75),
        ('2024-05-20', 'Yoga', 0.5)
    ]

    assert data["sleep"] == expected_sleep
    assert data["calories"] == expected_calories
    assert data["workouts"] == expected_workouts

    mock_get_records.assert_any_call(user_id, "sleep", 7, 'telegram_tracker_bot/db/tracker_data_base.db')
    mock_get_records.assert_any_call(user_id, "calories", 7, 'telegram_tracker_bot/db/tracker_data_base.db')
    mock_get_records.assert_any_call(user_id, "workouts", 7, 'telegram_tracker_bot/db/tracker_data_base.db')


@patch('telegram_tracker_bot.logic.stats.get_records_last_n_days')
def test_get_data_for_advice_no_data(mock_get_records):
    mock_get_records.side_effect = [[], [], []]
    user_id = 999
    data = get_data_for_advice(user_id)

    assert data["sleep"] == []
    assert data["calories"] == []
    assert data["workouts"] == []