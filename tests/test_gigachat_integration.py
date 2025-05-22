import pytest
from unittest.mock import patch, MagicMock
from telegram_tracker_bot.integrations import get_gigachat_advice
from telegram_tracker_bot.integrations.gigachat_integration import (
    prompt_template
)


@pytest.fixture
def mock_get_data():
    with patch(
            'telegram_tracker_bot.integrations'
            '.gigachat_integration.get_data_for_advice'
    ) as mock:
        yield mock


@pytest.fixture
def mock_llm():
    mock = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Моковый совет от GigaChat"
    mock.invoke.return_value = mock_response
    with patch(
            'telegram_tracker_bot.integrations.gigachat_integration.llm',
            new=mock
    ) as mock:
        yield mock


def test_get_gigachat_advice_success(mock_get_data, mock_llm):
    """Тест успешного получения совета от GigaChat с полными данными."""
    test_user_id = 123
    test_data = {
        "sleep": [("2023-01-01", 7.5), ("2023-01-02", 6.8)],
        "calories": [("2023-01-01", 2000), ("2023-01-02", 1800)],
        "workouts": [
            ("2023-01-01", "Бег", 1.0),
            ("2023-01-02", "Йога", 0.5)
        ]
    }
    mock_get_data.return_value = test_data
    mock_llm.invoke.return_value.content = "Тестовый совет от GigaChat"
    result = get_gigachat_advice(test_user_id)
    mock_get_data.assert_called_once_with(test_user_id)
    mock_llm.invoke.assert_called_once()
    prompt_arg = mock_llm.invoke.call_args[0][0]
    assert str(test_user_id) in prompt_arg
    assert "7.5 ч" in prompt_arg
    assert "2000 ккал" in prompt_arg
    assert "Бег (1.0 ч)" in prompt_arg
    assert result == "Тестовый совет от GigaChat"


def test_get_gigachat_advice_no_data(mock_get_data, mock_llm):
    """Тест обработки случая, когда нет данных."""
    test_user_id = 123
    test_data = {"sleep": [], "calories": [], "workouts": []}

    mock_get_data.return_value = test_data
    mock_llm.invoke.return_value.content = "Совет при отсутствии данных"

    result = get_gigachat_advice(test_user_id)

    prompt_arg = mock_llm.invoke.call_args[0][0]
    assert all(phrase in prompt_arg
               for phrase in ["Нет данных.",
                              "Сон:", "Калории:", "Тренировки:"])
    assert result == "Совет при отсутствии данных"


def test_get_gigachat_advice_partial_data(mock_get_data, mock_llm):
    """Тест обработки частичных данных."""
    test_user_id = 123
    test_data = {
        "sleep": [("2023-01-01", 7.5)],
        "calories": [],
        "workouts": [("2023-01-02", "Йога", 0.5)]
    }

    mock_get_data.return_value = test_data
    mock_llm.invoke.return_value.content = "Совет при частичных данных"

    result = get_gigachat_advice(test_user_id)

    prompt_arg = mock_llm.invoke.call_args[0][0]
    assert "7.5 ч" in prompt_arg
    assert "Нет данных." in prompt_arg
    assert "Йога (0.5 ч)" in prompt_arg
    assert result == "Совет при частичных данных"


def test_get_gigachat_advice_llm_error(mock_get_data, mock_llm):
    """Тест обработки ошибки GigaChat API."""
    test_user_id = 123
    test_data = {
        "sleep": [("2023-01-01", 7.5)],
        "calories": [("2023-01-01", 2000)],
        "workouts": []
    }

    mock_get_data.return_value = test_data
    mock_llm.invoke.side_effect = ValueError("API error")

    result = get_gigachat_advice(test_user_id)

    assert result == "Произошла ошибка при обращении к GigaChat."
    mock_llm.invoke.assert_called_once()


def test_prompt_template_structure():
    """Тест структуры шаблона промпта."""
    assert set(prompt_template.input_variables) == {
        "user_id", "sleep_data", "calories_data", "workouts_data"
    }

    template = prompt_template.template
    required_phrases = [
        "ID пользователя:",
        "Сон:",
        "Калории:",
        "Тренировки:",
        "Твой совет:"
    ]
    assert all(phrase in template for phrase in required_phrases)
