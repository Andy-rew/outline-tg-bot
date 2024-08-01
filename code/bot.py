import pandas as pd
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.types import BotCommand, BotCommandScopeChat

from db_models import get_user_by_tg_id
from keys_service import get_admin_key_deletion_buttons, get_user_key_deletion_buttons, get_users_for_approve_buttons, \
    create_new_user_key, get_key_info, get_user_key_view_buttons
from user_service import new_user_start, approve_new_user
from config import ADMINS, BOT_TOKEN
from exceptions import BotExceptionHandler, AbobaError
from outline import get_outline_client
from utils import _join_text, _wrap_as_markdown, CallbackEnum
from statistic_service import get_statistics_for_admin, get_statistics_for_user

bot = AsyncTeleBot(BOT_TOKEN,
                   exception_handler=BotExceptionHandler())
client = get_outline_client()

admin_commands = [
    BotCommand(command='start', description='Start'),
    BotCommand(command='admin_metrics', description='All keys statistic'),
    BotCommand(command='metrics', description='My keys statistic'),
    BotCommand(command='new_key', description='Add new key'),
    BotCommand(command='get_key',
               description='Get credentials for existing key'),
    BotCommand(command='users_for_approve', description='Get users for approve'),
    BotCommand(command='admin_delete_key', description='Delete old key'),
    BotCommand(command='delete_key', description='Delete old key'),
    BotCommand(command='help', description='Get help')
]

user_commands = [
    BotCommand(command='start', description='Start'),
    BotCommand(command='metrics', description='My keys statistic'),
    BotCommand(command='new_key', description='Add new key'),
    BotCommand(command='get_key',
               description='Get credentials for existing key'),
    BotCommand(command='delete_key', description='Delete old key'),
    BotCommand(command='help', description='Get help')
]


async def check_admin(message: types.Message, no_reply=False) -> bool:
    """
    Check if command was sent by admin or not
    :param no_reply:
    :param message: command
    :return: True if user is admin, False otherwise
    """
    if str(message.from_user.id) not in ADMINS:
        if not no_reply:
            await bot.reply_to(message, "Permission denied")
        return False
    return True


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

    await bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=message.chat.id))

    if await check_admin(message, True):
        await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=message.chat.id))
    elif await check_is_approved(message, True):
        await bot.set_my_commands(user_commands, scope=BotCommandScopeChat(chat_id=message.chat.id))


@bot.message_handler(func=check_admin, commands=['admin_metrics'])
async def admin_metrics_handler(message: types.Message) -> None:
    """
    Form all statistics DataFrame and send it to user
    :param message: command
    :return: None
    """

    str_res = get_statistics_for_admin()

    await bot.reply_to(message, _wrap_as_markdown(str_res),
                       parse_mode='Markdown')


@bot.message_handler(func=check_is_approved, commands=['metrics'])
async def metrics_handler(message: types.Message) -> None:
    """
    Form user statistics DataFrame and send it to user
    :param message: command
    :return: None
    """

    str_res = get_statistics_for_user(message.from_user.id)

    await bot.reply_to(message, _wrap_as_markdown(str_res),
                       parse_mode='Markdown')


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
        await bot.reply_to(message, f'{err}')
        return

    text = _join_text('Success creation', f'ID: {key.key_id}',
                      f'Name: {key.name}', 'Key in next message:')
    await bot.send_message(message.from_user.id, text)
    await bot.send_message(message.from_user.id,
                           _wrap_as_markdown(key.access_url),
                           parse_mode='Markdown')
    if message.chat.type != "private":
        await bot.reply_to(message, "Credentials sent to your DM.")


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

    await bot.send_message(message.chat.id, "Choose key to view",
                           reply_markup=markup)


@bot.message_handler(func=check_admin, commands=['admin_delete_key'])
async def admin_delete_key_handler(message: types.Message) -> None:
    """
    Try to delete old key from OutlineVPN server
    :param message: command
    :return: None
    """
    markup = types.InlineKeyboardMarkup(row_width=1)

    buttons = get_admin_key_deletion_buttons(message.from_user.id)
    markup.add(*buttons)

    await bot.send_message(message.chat.id, "Choose key for deletion",
                           reply_markup=markup)


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

    await bot.send_message(message.chat.id, "Choose key for deletion",
                           reply_markup=markup)


@bot.message_handler(func=check_admin, commands=['users_for_approve'])
async def get_users_for_approve_handler(message: types.Message) -> None:
    """
    Try to delete old key from OutlineVPN server
    :param message: command
    :return: None
    """
    markup = types.InlineKeyboardMarkup(row_width=1)

    buttons = get_users_for_approve_buttons(message.from_user.id)
    markup.add(*buttons)

    await bot.send_message(message.chat.id, "Choose user for approve",
                           reply_markup=markup)


def query_callback(call: types.CallbackQuery) -> bool:
    return True


@bot.callback_query_handler(func=query_callback)
async def callback_query_handler(call: types.CallbackQuery) -> None:
    """
    Handle pressing button for action on key
    :param call: Pressed button
    :return: None
    """
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id

    action = call.data.split(' ')[0]
    query_worker_id = call.data.split(' ')[1]

    if query_worker_id != str(call.from_user.id):
        await bot.answer_callback_query(call.id, "Permission denied")
        return

    if action not in CallbackEnum.__members__:
        await bot.answer_callback_query(call.id, "Action not found")

    if action == CallbackEnum.delete_key.value:
        data_id = call.data.split(' ')[2]

        delete_status_ok = client.delete_key(data_id)

        if delete_status_ok:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text=f'Success deletion\nID: {data_id}')
            await bot.answer_callback_query(call.id, "Done")
        else:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text="Failed deletion")
            await bot.answer_callback_query(call.id, "Failed")

    elif action == CallbackEnum.approve_user.value:
        data_id = call.data.split(' ')[2]

        approved_user = approve_new_user(data_id)
        approve_status_ok = approved_user.is_approved

        if approve_status_ok:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text=f'Success approve\nID: {data_id}')
            await bot.answer_callback_query(call.id, "Done")

            sent_message = await bot.send_message(approved_user.tg_id,
                                                  f"You are approved by admin and can create {approved_user.keys_count} VPN keys")

            await bot.set_my_commands(user_commands, scope=BotCommandScopeChat(chat_id=sent_message.chat.id))

        else:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text="Failed approve")
            await bot.answer_callback_query(call.id, "Failed")

    elif action == CallbackEnum.view_key.value:

        data_id = call.data.split(' ')[2]
        try:
            key = get_key_info(query_worker_id, data_id)
        except AbobaError as err:
            await bot.answer_callback_query(call.id, f"{err}")
            return

        text = _join_text('Got key', f'ID: {key.key_id}',
                          f'Name: {key.name}', 'Key in next message:')
        await bot.send_message(query_worker_id, text)
        await bot.send_message(query_worker_id,
                               _wrap_as_markdown(key.access_url),
                               parse_mode='Markdown')
        if message.chat.type != "private":
            await bot.answer_callback_query(call.id, "Credentials sent to your DM.")

        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text=f'Success')

    elif action == CallbackEnum.cancel.value:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text='Canceled')
        await bot.answer_callback_query(call.id, "Canceled")


@bot.message_handler(commands=['help'])
async def help_handler(message: types.Message) -> None:
    """
    Show help string
    :param message: command
    :return: None
    """
    await bot.reply_to(message, "Use commands to manage OutlineVPN server")


async def run_bot() -> None:
    """
    Make commands and start bot
    :return: None
    """

    commands = [
        BotCommand(command='start', description='Start'),
    ]

    await bot.set_my_commands(commands=commands)

    await bot.infinity_polling()
