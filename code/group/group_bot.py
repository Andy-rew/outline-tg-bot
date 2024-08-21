from telebot import types
from telebot.async_telebot import AsyncTeleBot

from code.config import GROUP_BOT_TOKEN
from code.config_commands import group_commands
from code.exceptions import BotExceptionHandler
from code.statistic_service import get_statistics_for_admin
from code.utils import _wrap_as_markdown

bot = AsyncTeleBot(GROUP_BOT_TOKEN, exception_handler=BotExceptionHandler())


@bot.message_handler(commands=['help'])
async def help_handler(message: types.Message) -> None:
    """
    Show help string
    :param message: command
    :return: None
    """
    await bot.reply_to(message, "Use commands to manage OutlineVPN server")


@bot.message_handler(commands=['metrics'])
async def admin_metrics_handler(message: types.Message) -> None:
    """
    Form all statistics DataFrame and send it to user
    :param message: command
    :return: None
    """

    str_res = get_statistics_for_admin()

    await bot.reply_to(message, _wrap_as_markdown(str_res), parse_mode='Markdown')


async def run_group_bot() -> None:
    """
    Make commands and start bot
    :return: None
    """

    await bot.set_my_commands(commands=group_commands)

    await bot.infinity_polling()
