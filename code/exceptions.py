from telebot.async_telebot import ExceptionHandler


class OutlineServerErrorException(Exception):
    """Outline API returned error"""
    pass


class AbobaError(Exception):
    """Something went wrong"""
    pass


class BotExceptionHandler(ExceptionHandler):
    async def handle(self, exception):
        print(f'ROFL: {exception}')
