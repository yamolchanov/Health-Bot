"""
Модуль содержит асинхронные обработчики команд и вспомогательные функции
для Telegram-бота по отслеживанию здоровья пользователя.

Функционал включает:
- Запись данных о сне (/sleep)
- Запись данных о потребленных калориях (/calories)
- Запись данных о тренировках (/workout)
- Отправка текстовой статистики за последние 7 дней (/stats)
- Генерация и отправка графика активности (/plot)
- Получение и отправка советов от ИИ (/advice)
- Отправка мотивационных сообщений (/motivation)
- Помощь и стартовые сообщения (/start, /help)
- Логирование ошибок

Используются внешние модули для работы с данными и интеграции с GigaChat.
"""
import logging
import datetime
import re
from sqlite3 import DatabaseError
from typing import Optional
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from telegram_tracker_bot.logic import format_timedelta
from telegram_tracker_bot.db import (add_sleep_record, add_calories_record,
                                     add_workout_record)
from telegram_tracker_bot.logic import (get_weekly_stats_text,
                                        plot_weekly_data,
                                        get_random_motivation)
from telegram_tracker_bot.integrations import get_gigachat_advice

logging.basicConfig(
    format='%(asctime)s'
           ' - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_duration(text: str) -> Optional[float]:
    """
    Парсит строку времени в формат часов.

    Поддерживает форматы:
        - 'ЧЧ:ММ' (часы и минуты, например, '02:30')
        - 'Ч.ДЧ' (десятичные часы, например, '2.5')

    Args:
        text (str): Время в строковом формате.

    Returns:
        Optional[float]: Продолжительность в часах.
    """
    match_colon = re.fullmatch(r'(\d{1,2}):(\d{1,2})', text)
    if match_colon:
        hours = int(match_colon.group(1))
        minutes = int(match_colon.group(2))
        if 0 <= hours < 24 and 0 <= minutes < 60:
            return hours + minutes / 60.0
        return None
    match_decimal = re.fullmatch(
        r'(\d{1,2}(?:[.,]\d+)?)', text.replace(',', '.'))
    if match_decimal:
        try:
            hours = float(match_decimal.group(1))
            if 0 <= hours < 24:
                return hours
            return None
        except ValueError:
            return None
    return None


async def start(update: Update) -> None:
    """
    Отправляет приветственное сообщение при команде /start.

    Args:
        update (Update): Объект обновления от Telegram.
    """
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.name}!"
        " Я твой помощник для отслеживания сна, калорий и тренировок.\n\n"
        "Используй команды:\n"
        "😴 /sleep ЧАСЫ - Записать сон\n (например /sleep 8:15)\n"
        "🍎 /calories КОЛ-ВО - Записать калории\n (например /calories 1800)\n"
        "💪 /workout ЧАСЫ АКТИВНОСТЬ - Записать тренировку\n"
        " (например /workout 2:30 Вольная борьба)\n"
        "📊 /stats - Показать статистику за 7 дней\n"
        "📈 /plot - Показать график за 7 дней\n"
        "💡 /advice - Получить совет от ИИ\n"
        "🚀 /motivation - Получить мотивационное сообщение\n"
        "❓ /help - Показать это сообщение"
    )


async def help_command(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправляет справку по командам пользователю.

    Args:
        update (Update): Объект обновления.
        context (ContextTypes.DEFAULT_TYPE) : объект состояния.
    """
    _ = context
    await update.message.reply_text(
        "Доступные команды:\n"
        "/sleep ЧАСЫ - Записать сон (напр. /sleep 8:15)\n"
        "/calories КОЛ-ВО - Записать калории (напр. /calories 1800)\n"
        "/workout ЧАСЫ АКТИВНОСТЬ - Записать тренировку"
        " (напр., /workout 1:30 Бег)\n"
        "/stats - Показать статистику за 7 дней\n"
        "/plot - Показать график за 7 дней\n"
        "/advice - Получить совет от ИИ\n"
        "/motivation - Получить мотивационное сообщение\n"
        "/help - Показать эту справку"
    )


async def record_sleep(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает команду пользователя для записи данных о сне.

    Args:
        update (Update): Объект обновления.
        context (ContextTypes.DEFAULT_TYPE): Контекст вызова.

    Returns:
        None
    """
    user_id = update.effective_user.id
    today_str = datetime.date.today().strftime('%Y-%m-%d')

    if not context.args:
        await update.message.reply_text(
            "Пожалуйста, укажите длительность сна после команды."
            " Пример: /sleep 7.5")
        return

    duration_str = context.args[0]
    hours = parse_duration(duration_str)

    if hours is None or hours <= 0:
        await update.message.reply_text(
            "Некорректный формат или значение времени сна."
            " Используйте ЧЧ:ММ (напр., 8:15)."
            " Значение должно быть положительным.")
        return

    try:
        add_sleep_record(user_id, today_str,
                         hours,
                         'telegram_tracker_bot/db/tracker_data_base.db')
        await update.message.reply_text(
            f"✅ Запись о сне ({format_timedelta(hours)})"
            f" на {today_str} добавлена!")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_random_motivation())
    except DatabaseError as e:
        logger.error("Ошибка при записи сна для user %s: %s", user_id, e)
        await update.message.reply_text(
            "Произошла ошибка при сохранении данных."
            " Попробуйте позже.")


async def record_calories(update: Update,
                          context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает команду.

    Args:
        update (Update): Объект обновления.
        context (ContextTypes.DEFAULT_TYPE): Контекст вызова.

    Returns:
        None
    """
    user_id = update.effective_user.id
    today_str = datetime.date.today().strftime('%Y-%m-%d')

    if not context.args:
        await update.message.reply_text(
            "Пожалуйста, укажите количество калорий после команды."
            " Пример: `/calories 1800`")
        return

    try:
        amount = int(context.args[0])
        if amount <= 0:
            await update.message.reply_text(
                "Количество калорий должно быть положительным числом."
                )
            return
    except (ValueError, IndexError):
        await update.message.reply_text(
            "Некорректное значение калорий."
            " Пожалуйста, введите целое число."
        )
        return

    try:
        add_calories_record(user_id,
                            today_str,
                            amount,
                            'telegram_tracker_bot/db/tracker_data_base.db')
        await update.message.reply_text(
            f"✅ Запись о калориях ({amount} ккал)"
            f" на {today_str} добавлена!")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_random_motivation())
    except DatabaseError as e:
        logger.error("Ошибка при записи калорий для user %s: %s", user_id, e)
        await update.message.reply_text(
            "Произошла ошибка при сохранении данных."
            " Попробуйте позже.")


async def record_workout(update: Update,
                         context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает команду пользователя для записи данных о тренировке.

    Args:
        update (Update): Объект обновления Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст вызов.

    Returns:
        None
    """
    user_id = update.effective_user.id
    today_str = datetime.date.today().strftime('%Y-%m-%d')

    if len(context.args) < 2:
        await update.message.reply_text(
            "Использование: /workout ВРЕМЯ ТИП_АКТИВНОСТИ"
            "\nПример: /workout 1:30 Бег")
        return

    duration_str = context.args[0]
    activity_type = " ".join(context.args[1:]).strip().capitalize()
    duration_hours = parse_duration(duration_str)
    if duration_hours is None or duration_hours <= 0:
        await update.message.reply_text(
            "Некорректный формат или значение времени тренировки."
            " Используйте ЧЧ:ММ (напр., 0:45)."
            " Значение должно быть положительным.")
        return

    if not activity_type:
        await update.message.reply_text("Пожалуйста, укажите тип активности.")
        return

    try:
        add_workout_record(user_id,
                           today_str,
                           duration_hours,
                           activity_type,
                           'telegram_tracker_bot/db/tracker_data_base.db')
        await update.message.reply_text(
            f"✅ Тренировка '{activity_type}'"
            f" ({format_timedelta(duration_hours)})"
            f" на {today_str} записана!")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_random_motivation())
    except DatabaseError as e:
        logger.error("Ошибка при записи"
                     " тренировок для user %s: %s", user_id, e)
        await update.message.reply_text(
            "Произошла ошибка при сохранении данных."
            " Попробуйте позже.")


async def show_stats(update: Update,
                     context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправляет пользователю текстовую статистику за последние 7 дней.

    Args:
        update (Update): Объект обновления Telegram.
        context (ContextTypes.DEFAULT_TYPE) : объект состояния.
    """
    _ = context
    user_id = update.effective_user.id
    try:
        stats_text = get_weekly_stats_text(user_id)
        await update.message.reply_text(stats_text, parse_mode='HTML')
    except DatabaseError as e:
        logger.error("Ошибка при получении статистики"
                     " для user %s: %s", user_id, e)
        await update.message.reply_text(
            "Не удалось получить статистику."
            " Попробуйте позже.")


async def send_plot(update: Update,
                    context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Генерирует график с данными за последние 7 дней
    и отправляет его пользователю.

    Args:
        update (Update): Объект обновления Telegram.
        context (ContextTypes.DEFAULT_TYPE) : объект состояния.
    """
    _ = context
    user_id = update.effective_user.id
    await update.message.reply_text("📈 Генерирую график...")

    try:
        plot_buffer = plot_weekly_data(user_id)
        if plot_buffer:
            await update.message.reply_photo(
                photo=InputFile(
                    plot_buffer,
                    filename=f'stats_{user_id}_{datetime.date.today()}.png'
                ),
                caption="Ваш график активности за последние 7 дней.")
        else:
            await update.message.reply_text(
                "Нет данных для построения графика за последние 7 дней."
                " Запишите данные с помощью команд"
                " /sleep, /calories, /workout.")
    except DatabaseError as e:
        logger.error("Ошибка при генерации"
                     " графика для user %s: %s", user_id, e)
        await update.message.reply_text(
            "Не удалось создать или отправить график."
            " Попробуйте позже.")


async def send_advice(update: Update,
                      context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Получает персональный совет от GigaChat на основе данных пользователя
    и отправляет его в чат.

    Args:
        update (Update): Объект обновления Telegram.
        context (ContextTypes.DEFAULT_TYPE) : объект состояния.
    """
    _ = context
    user_id = update.effective_user.id
    await update.message.reply_text("💡 Запрашиваю совет у ИИ...")

    try:
        advice = get_gigachat_advice(user_id)
        if advice:
            await update.message.reply_text(
                f"🧠 Совет от GigaChat:"
                f"\n\n{advice}")
        else:
            await update.message.reply_text(
                "Не удалось получить совет в этот раз."
            )
    except DatabaseError as e:
        logger.error("Ошибка при получении совета для user %s: %s", user_id, e)
        await update.message.reply_text(
            "Произошла ошибка при получении совета."
        )


async def send_motivation(update: Update,
                          context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправляет пользователю случайное мотивационное сообщение.

    Args:
        update (Update): Объект обновления Telegram.
        context (ContextTypes.DEFAULT_TYPE) : объект состояния.
    """
    _ = context
    message = get_random_motivation()
    await update.message.reply_text(f"🚀 {message}")


async def error_handler(
        update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Логирует ошибки, возникшие при обработке обновлений.

    Args:
        update (object): Объект обновления, в ходе.
        context (ContextTypes.DEFAULT_TYPE) : объект состояния.
    """
    _ = context
    logger.error("Исключение при обработке"
                 " обновления %s", update, exc_info=True)
