"""
Основной модуль запуска Telegram-бота для отслеживания сна,
калорий и тренировок.

Здесь происходит настройка и запуск бота:
- Подключение к Telegram API через токен
- Регистрация обработчиков команд
- Настройка парсинга сообщений в HTML формате
- Логирование ключевых событий (запуск, ошибки, остановка)

Команды бота включают:
/start, /help, /sleep, /calories, /workout, /stats, /plot, /advice, /motivation

После запуска бот начинает прослушивать обновления в режиме polling.
"""

import logging
from telegram.ext import CommandHandler, ApplicationBuilder, Defaults
from telegram.constants import ParseMode
from telegram_tracker_bot.db import initialize_db
from telegram_tracker_bot.handlers import (start, help_command, record_sleep,
                                           record_calories, record_workout,
                                           show_stats, send_plot, send_advice,
                                           send_motivation, error_handler)
from telegram_tracker_bot.config import TELEGRAM_BOT_TOKEN

initialize_db('telegram_tracker_bot/db/tracker_data_base.db')
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

"""Запускает бота."""
logger.info("Запуск бота...")

defaults = Defaults(parse_mode=ParseMode.HTML)
application = (ApplicationBuilder()
               .token(TELEGRAM_BOT_TOKEN)
               .defaults(defaults).build())

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("sleep", record_sleep))
application.add_handler(CommandHandler("calories", record_calories))
application.add_handler(CommandHandler("workout", record_workout))
application.add_handler(CommandHandler("stats", show_stats))
application.add_handler(CommandHandler("plot", send_plot))
application.add_handler(CommandHandler("advice", send_advice))
application.add_handler(CommandHandler("motivation", send_motivation))

application.add_error_handler(error_handler)
logger.info("Бот готов к работе.")
application.run_polling()
logger.info("Бот остановлен.")
# запуск тестов PYTHONPATH=. pytest --cov=telegram_tracker_bot