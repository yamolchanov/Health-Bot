"""
Оформляет модуль с логикой команд ТГ-Бота.
"""

from .plotting import plot_weekly_data
from .motivation import get_random_motivation

from .stats import (
    format_timedelta,
    get_weekly_stats_text,
    get_data_for_advice,
)

__all__ = ['plot_weekly_data', 'get_random_motivation',
           'format_timedelta', 'get_weekly_stats_text',
           'get_data_for_advice']
