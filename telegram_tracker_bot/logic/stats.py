"""
Модуль для обработки и формирования отчетов
 по недельной активности пользователя.

Функции:
- format_timedelta(hours: float) -> str:
    Форматирует часы в строку вида "ЧЧ:ММ".

- get_weekly_stats_text(user_id: int) -> str:
    Генерирует текстовый отчет со статистикой сна, калорий и тренировок
    за последние 7 дней для указанного пользователя.

- get_data_for_advice(user_id: int) -> dict:
    Собирает и возвращает данные за последнюю неделю в упрощенном формате,
    пригодном для передачи в ИИ-сервис GigaChat
     для анализа и формирования советов.

Использует:
- telegram_tracker_bot для получения записей пользователя.
- collections.defaultdict для агрегации данных по типам активности.
"""

from collections import defaultdict
from telegram_tracker_bot.db import get_records_last_n_days


def format_timedelta(hours: float) -> str:
    """
    Форматирует часы (float) в строку ЧЧ:ММ.

    Args:
        hours (float): Принимает на вход время.

    Returns:
        str: Время
    """
    total_minutes = int(hours * 60)
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h:02d}:{m:02d}"


def get_weekly_stats_text(user_id: int) -> str:
    """
    Генерирует текстовый отчет по статистике за последние 7 дней.

    Args:
        user_id (int): Идентификатор пользователя.

    Returns:
        str: Текстовый формат статистики за неделю.
    """
    sleep_data = get_records_last_n_days(user_id,
                                         "sleep", 7,
                                         'telegram_tracker_bot'
                                         '/db/tracker_data_base.db')
    calories_data = get_records_last_n_days(user_id, "calories", 7,
                                            'telegram_tracker_bot/'
                                            'db/tracker_data_base.db')
    workouts_data = get_records_last_n_days(user_id, "workouts", 7,
                                            'telegram_tracker_bot/db/'
                                            'tracker_data_base.db')

    report = ["📊 Статистика за последние 7 дней:\n"]
    if sleep_data:
        total_sleep = sum(item['hours'] for item in sleep_data)
        avg_sleep = total_sleep / len(sleep_data)
        report.append("😴 Сон:")
        report.append(f"  - В среднем: {format_timedelta(avg_sleep)} / ночь")
        report.append("  - Записи:")
        for entry in sorted(sleep_data, key=lambda x: x['date']):
            report.append(
                f"    - {entry['date']}:"
                f" {format_timedelta(entry['hours'])}"
            )
    else:
        report.append("😴 Сон: Нет данных за последние 7 дней.")

    report.append("\n")

    if calories_data:
        total_calories = sum(item['amount'] for item in calories_data)
        avg_calories = total_calories / len(calories_data)
        report.append("🍎 Калории:")
        report.append(f"  - В среднем: {avg_calories:.0f} ккал / день")
        report.append("  - Записи:")
        for entry in sorted(calories_data, key=lambda x: x['date']):
            report.append(f"    - {entry['date']}: {entry['amount']} ккал")
    else:
        report.append("🍎 Калории: Нет данных за последние 7 дней.")

    report.append("\n")

    if workouts_data:
        total_duration = sum(item['duration_hours'] for item in workouts_data)
        activities = defaultdict(float)
        for item in workouts_data:
            activities[item['activity_type']] += item['duration_hours']
        report.append("💪 Тренировки:")
        report.append(f"  - Всего часов: {format_timedelta(total_duration)}")
        report.append("  - По активностям:")
        for activity, duration in sorted(activities.items(),
                                         key=lambda item: item[1],
                                         reverse=True):
            report.append(f"    - {activity}: {format_timedelta(duration)}")
    else:
        report.append("💪 Тренировки: Нет данных за последние 7 дней.")

    return "\n".join(report)


def get_data_for_advice(user_id: int) -> dict:
    """
    Собирает данные за последнюю неделю для отправки в GigaChat.

    Args:
        user_id (int): Идентификатор пользователя.

    Returns:
        dict: Словарь с данными по активности пользователя за последнюю неделю.
    """
    sleep_data = get_records_last_n_days(
        user_id, "sleep", 7,
        'telegram_tracker_bot/db/tracker_data_base.db')
    calories_data = get_records_last_n_days(
        user_id, "calories", 7,
        'telegram_tracker_bot/db/tracker_data_base.db')
    workouts_data = get_records_last_n_days(
        user_id, "workouts", 7,
        'telegram_tracker_bot/db/tracker_data_base.db')

    simple_sleep = [(d['date'], d['hours']) for d in sleep_data]
    simple_calories = [(d['date'], d['amount']) for d in calories_data]
    simple_workouts = [(d['date'], d['activity_type'],
                        d['duration_hours'])
                       for d in workouts_data]

    return {
        "sleep": simple_sleep,
        "calories": simple_calories,
        "workouts": simple_workouts
    }
