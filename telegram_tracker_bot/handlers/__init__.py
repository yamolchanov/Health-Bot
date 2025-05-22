"""
Создает модуль для исполнения команд.
"""

from .handlers import (
    start,
    help_command,
    record_sleep,
    record_calories,
    record_workout,
    show_stats,
    send_plot,
    send_advice,
    send_motivation,
    error_handler,
    parse_duration
)

__all__ = [
    'start',
    'help_command',
    'record_sleep',
    'record_calories',
    'record_workout',
    'show_stats',
    'send_plot',
    'send_advice',
    'send_motivation',
    'error_handler',
    'parse_duration'
]
