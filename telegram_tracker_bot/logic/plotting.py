"""
Модуль для создания графиков недельной активности пользователя.

Функции:
- plot_weekly_data(user_id: int) -> BytesIO | None:
    Создает и возвращает график с данными за последнюю неделю по сну,
    калориям и тренировкам пользователя в виде изображения в памяти.
    Если данных нет, возвращает None.

Использует:
- matplotlib для построения графиков,
- telegram_tracker_bot для получения данных пользователя,
- вспомогательную функцию format_timedelta для форматирования времени.
"""

from typing import Optional
from io import BytesIO
import datetime
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib
from telegram_tracker_bot.db import get_records_last_n_days
from .stats import format_timedelta

matplotlib.use("Agg")


def plot_weekly_data(user_id: int) -> Optional[BytesIO]:
    """
    Создает график с данными за последнюю неделю и возвращает его как BytesIO.

    Args:
        user_id (int): Идентификатор пользователя.

    Returns:
        Optional[BytesIO]: График в виде объекта BytesIO.
    """
    sleep_data = get_records_last_n_days(user_id,
                                         "sleep",
                                         7,
                                         'telegram_tracker_bot'
                                         '/db/tracker_data_base.db')
    calories_data = get_records_last_n_days(user_id,
                                            "calories", 7,
                                            'telegram_tracker_bot/'
                                            'db/tracker_data_base.db')
    workouts_data = get_records_last_n_days(user_id,
                                            "workouts", 7,
                                            'telegram_tracker_bot/'
                                            'db/tracker_data_base.db')

    if not sleep_data and not calories_data and not workouts_data:
        return None
    dates = [
        datetime.date.today() - datetime.timedelta(days=i)
        for i in range(6, -1, -1)
    ]
    dates.sort()

    workouts_map = {d_str: 0.0
                    for d_str in [d.strftime("%Y-%m-%d")
                                  for d in dates]}
    for item in workouts_data:
        if item["date"] in workouts_map:
            workouts_map[item["date"]] += item["duration_hours"]
    sleep_values = [{item["date"]: item["hours"]
                     for item in sleep_data}.get(d_str, np.nan)
                    for d_str in
                    [d.strftime("%Y-%m-%d") for d in dates]]
    calories_values = [{item["date"]: item["amount"]
                        for item in calories_data}.get(d_str, np.nan)
                       for d_str in [d.strftime("%Y-%m-%d")
                                     for d in dates]]
    workout_values = [workouts_map.get(d_str, np.nan)
                      for d_str in [d.strftime("%Y-%m-%d")
                                    for d in dates]]

    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    fig.suptitle(f"Недельная активность (ID: {user_id})", fontsize=16)

    axes[0].plot(
        dates, sleep_values, marker="o",
        linestyle="-", color="blue",
        label="Сон (часы)"
    )
    axes[0].set_ylabel("Часы сна")
    axes[0].grid(True, linestyle="--", alpha=0.6)
    axes[0].legend()
    axes[0].yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x,
                          pos: format_timedelta(x) if not np.isnan(x) else "")
    )
    for i, txt in enumerate(sleep_values):
        if not np.isnan(txt):
            axes[0].annotate(
                format_timedelta(txt),
                (mdates.date2num(dates[i]), sleep_values[i]),
                textcoords="offset points",
                xytext=(0, 5),
                ha="center",
            )

    axes[1].plot(
        dates,
        calories_values,
        marker="s",
        linestyle="-",
        color="red",
        label="Калории (ккал)",
    )
    axes[1].set_ylabel("Калории (ккал)")
    axes[1].grid(True, linestyle="--", alpha=0.6)
    axes[1].legend()
    for i, txt in enumerate(calories_values):
        if not np.isnan(txt):
            axes[1].annotate(
                f"{int(txt)}",
                (mdates.date2num(dates[i]), calories_values[i]),
                textcoords="offset points",
                xytext=(0, 5),
                ha="center",
            )
    axes[2].bar(dates, workout_values, color="green",
                alpha=0.7, label="Тренировки (часы)")
    axes[2].set_ylabel("Часы тренировок")
    axes[2].grid(True, linestyle="--", alpha=0.6)
    axes[2].legend()
    axes[2].yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, pos: format_timedelta(x)
                          if not np.isnan(x) else "")
    )
    for i, txt in enumerate(workout_values):
        if not np.isnan(txt) and txt > 0:
            axes[2].annotate(
                format_timedelta(txt),
                (mdates.date2num(dates[i]), workout_values[i]),
                textcoords="offset points",
                xytext=(0, 5),
                ha="center",
            )
    plt.xlabel("Дата")
    fig.autofmt_xdate()
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    axes[2].xaxis.set_major_locator(mdates.DayLocator(interval=1))
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf
