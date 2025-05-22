"""
Конфигурационный модуль для Telegram-бота.

Содержит конфиденциальные данные и настройки:
- Токен бота Telegram
- Имя файла базы данных
- Ключи API и другие секреты

Важно:
Используйте файл .env для безопасности ключей,
 добавьте его в файл .gitignore,
  чтобы случайно не отправить его на удалённый репозиторий,
  где им смогут вспользоваться мошенники.
"""


import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GIGACHAT_CLIENT_ID = os.getenv('GIGACHAT_CLIENT_ID')
GIGACHAT_CLIENT_SECRET = os.getenv('GIGACHAT_CLIENT_SECRET')
GIGACHAT_TOKEN_URL = os.getenv('GIGACHAT_TOKEN_URL')
GIGACHAT_AUTHORIZATION_KEY = os.getenv('GIGACHAT_AUTHORIZATION_KEY')
DATABASE_NAME = 'telegram_tracker_bot/db/tracker_data_base.db'
