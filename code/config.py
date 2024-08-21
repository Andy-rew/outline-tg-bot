import os

from dotenv import dotenv_values

config = dotenv_values(".env")

if not config:
    config = os.environ

ADMIN_BOT_TOKEN: str = config.get('ADMIN_BOT_TOKEN')
USER_BOT_TOKEN: str = config.get('USER_BOT_TOKEN')
GROUP_BOT_TOKEN: str = config.get('GROUP_BOT_TOKEN')
API_URL: str = config.get('API_URL')
CERT_SHA256: str = config.get('CERT_SHA256')
ADMINS: [str] = config.get('ADMINS').split(',')
IS_MOCK_OUTLINE: bool = config.get('MOCK_OUTLINE') == 'true'

DB_HOST: str = config.get('DB_HOST')
DB_PORT: int = int(config.get('DB_PORT'))
POSTGRES_USERNAME: str = config.get('POSTGRES_USERNAME')
POSTGRES_PASSWORD: str = config.get('POSTGRES_PASSWORD')
POSTGRES_DATABASE: str = config.get('POSTGRES_DATABASE')

RECREATE_DB_ON_START: bool = config.get('RECREATE_DB_ON_START') == 'true'

KEYS_COUNT: str = config.get('KEYS_COUNT')
