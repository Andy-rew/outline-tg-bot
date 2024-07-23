from telebot.async_telebot import ExceptionHandler


class AbobaError(Exception):
    """Something went wrong"""


class BotExceptionHandler(ExceptionHandler):
    async def handle(self, exception):
        print(f'ROFL: {exception}')
