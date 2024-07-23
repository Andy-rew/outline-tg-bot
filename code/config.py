import os

from dotenv import dotenv_values

config = dotenv_values("../.env")

if not config:
    config = os.environ

BOT_TOKEN: str = config.get('BOT_TOKEN')
API_URL: str = config.get('API_URL')
CERT_SHA256: str = config.get('CERT_SHA256')
ADMINS: [str] = config.get('ADMINS').split(',')
IS_MOCK_OUTLINE: bool = config.get('MOCK_OUTLINE') == 'true'