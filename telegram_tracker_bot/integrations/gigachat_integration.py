"""
Оформляет модуль логики интеграции GigaChat в ТГ-Бота.
"""

from langchain_gigachat import GigaChat
from langchain_core.prompts import PromptTemplate
from telegram_tracker_bot.logic import get_data_for_advice
from telegram_tracker_bot.config import GIGACHAT_AUTHORIZATION_KEY

llm = GigaChat(
    credentials=GIGACHAT_AUTHORIZATION_KEY,
    model="GigaChat",
    scope="GIGACHAT_API_PERS",
    verify_ssl_certs=False
)

prompt_template = PromptTemplate(
    input_variables=["user_id", "sleep_data",
                     "calories_data", "workouts_data"],
    template="""
Проанализируй данные о здоровье пользователя за
 последнюю неделю и дай краткий, дельный совет.

ID пользователя: {user_id}

Сон:
{sleep_data}

Калории:
{calories_data}

Тренировки:
{workouts_data}

Твой совет:
""",
)


def get_gigachat_advice(user_id: int) -> str:
    """
    Получает ответ AI для пользователя на основе его данных.

    Args:
        user_id: int - ID пользователя

    Returns:
        str: совет для пользователя
    """
    data = get_data_for_advice(user_id)

    sleep_data = (
        "\n".join(f"- {date}:"
                  f" {hours:.1f} ч" for date, hours in data.get("sleep", []))
        if data.get("sleep") else "Нет данных."
    )

    calories_data = (
        "\n".join(f"- {date}:"
                  f" {amount} ккал"
                  for date, amount in data.get("calories", []))
        if data.get("calories") else "Нет данных."
    )

    workouts_data = (
        "\n".join(f"- {date}:"
                  f" {activity} ({duration:.1f} ч)"
                  for date, activity, duration in data.get("workouts", []))
        if data.get("workouts") else "Нет данных."
    )

    final_prompt = prompt_template.format(
        user_id=user_id,
        sleep_data=sleep_data,
        calories_data=calories_data,
        workouts_data=workouts_data
    )

    try:
        response = llm.invoke(final_prompt)
        return response.content
    except ValueError as e:
        print(f"[GigaChat ERROR]: {e}")
        return "Произошла ошибка при обращении к GigaChat."
