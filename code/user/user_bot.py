from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.types import BotCommandScopeChat, BotCommand

from code.callback_resolver import resolve_callback
from code.config import USER_BOT_TOKEN
from code.config_commands import user_commands
from code.db_models import get_user_by_tg_id
from code.exceptions import BotExceptionHandler, AbobaError
from code.keys_service import create_new_user_key, get_user_key_view_buttons, get_user_key_deletion_buttons
from code.statistic_service import get_statistics_for_user
from code.user_service import new_user_start
from code.utils import _wrap_as_markdown, _join_text

bot = AsyncTeleBot(USER_BOT_TOKEN, exception_handler=BotExceptionHandler())


async def check_is_approved(message: types.Message, no_reply=False) -> bool:
    """
    Check if user is approved
    :param no_reply:
    :param message: command
    :return: True if user is approved, False otherwise
    """
    user = get_user_by_tg_id(message.from_user.id)

    if not user or user.is_approved is False:
        if not no_reply:
            await bot.reply_to(message, "Permission denied")
        return False
    return True


@bot.message_handler(commands=['start'])
async def start_handler(message: types.Message) -> None:
    """
    Show greeting to user
    :param message: command
    :return: None
    """

    await bot.reply_to(message, 'Welcome to Outline, body!')

    try:
        new_user_start(message.from_user.id, message.from_user.first_name)
    except AbobaError as err:
        await bot.reply_to(message, f'{err}')

    await bot.delete_my_commands(
        scope=BotCommandScopeChat(chat_id=message.chat.id))

    if await check_is_approved(message, True):
        await bot.set_my_commands(user_commands, scope=BotCommandScopeChat(chat_id=message.chat.id))


@bot.message_handler(func=check_is_approved, commands=['metrics'])
async def metrics_handler(message: types.Message) -> None:
    """
    Form user statistics DataFrame and send it to user
    :param message: command
    :return: None
    """

    str_res = get_statistics_for_user(message.from_user.id)

    await bot.reply_to(message, _wrap_as_markdown(str_res), parse_mode='Markdown')


@bot.message_handler(func=check_is_approved, commands=['new_key'])
async def new_key_handler(message: types.Message) -> None:
    """
    Try to create a new key in OutlineVPN server
    :param message: command and new key name
    :return: None
    """
    try:
        new_key = message.text.split()[1]
    except IndexError:
        await bot.reply_to(message, "Key name is not valid")
        return

    try:
        key = create_new_user_key(message.from_user.id, new_key)
    except AbobaError as err:
        await bot.reply_to(message, str(err))
        return

    text = _join_text('Success creation', f'ID: {key.key_id}', f'Name: {key.name}', 'Key in next message:')
    await bot.send_message(message.from_user.id, text)
    await bot.send_message(message.from_user.id, _wrap_as_markdown(key.access_url), parse_mode='Markdown')


@bot.message_handler(func=check_is_approved, commands=['get_key'])
async def get_key_handler(message: types.Message) -> None:
    """
    Try to get credentials for existing key in OutlineVPN server
    :param message: command and new key name
    :return: None
    """
    markup = types.InlineKeyboardMarkup(row_width=1)

    buttons = get_user_key_view_buttons(message.from_user.id)
    markup.add(*buttons)

    await bot.send_message(message.chat.id, "Choose key to view", reply_markup=markup)


@bot.message_handler(func=check_is_approved, commands=['delete_key'])
async def delete_key_handler(message: types.Message) -> None:
    """
    Try to delete old key from OutlineVPN server
    :param message: command
    :return: None
    """
    markup = types.InlineKeyboardMarkup(row_width=1)

    buttons = get_user_key_deletion_buttons(message.from_user.id)
    markup.add(*buttons)

    await bot.send_message(message.chat.id, "Choose key for deletion", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
async def callback_query_handler(call: types.CallbackQuery) -> None:
    """
    Handle pressing button for action on key
    :param call: Pressed button
    :return: None
    """
    await resolve_callback(bot, call)


@bot.message_handler(commands=['help'])
async def help_handler(message: types.Message) -> None:
    """
    Show help string
    :param message: command
    :return: None
    """
    await bot.reply_to(message, "Use commands to manage OutlineVPN server")


async def run_user_bot() -> None:
    """
    Make commands and start bot
    :return: None
    """

    commands = [
        BotCommand(command='start', description='Start'),
    ]

    await bot.set_my_commands(commands=commands)

    await bot.infinity_polling()
