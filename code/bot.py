import pandas as pd
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.types import BotCommand

from keys_service import get_admin_key_deletion_buttons, get_user_key_deletion_buttons, get_users_for_approve_buttons, \
    create_new_user_key
from user_service import new_user_start, approve_new_user
from config import ADMINS, BOT_TOKEN
from exceptions import BotExceptionHandler, OutlineServerErrorException
from outline import get_outline_client
from utils import _join_text, _wrap_as_markdown, create_deletion_keys_buttons, CallbackEnum
from statistic_service import get_statistics_for_admin, get_statistics_for_user

bot = AsyncTeleBot(BOT_TOKEN,
                   exception_handler=BotExceptionHandler())
client = get_outline_client()


def check_admin(message: types.Message) -> bool:
    """
    Check if command was sent by admin or not
    :param message: command
    :return: True if user is admin, False otherwise
    """
    if str(message.from_user.id) not in ADMINS:
        bot.reply_to(message, "Permission denied")
        return False
    return True


@bot.message_handler(commands=['start'])
async def start_handler(message: types.Message) -> None:
    """
    Show greeting to user
    :param message: command
    :return: None
    """

    new_user_start(message.from_user.id, message.from_user.first_name)
    await bot.reply_to(message, 'Welcome to Outline, body!')


@bot.message_handler(func=check_admin, commands=['admin_metrics'])
async def metrics_handler(message: types.Message) -> None:
    """
    Form all statistics DataFrame and send it to user
    :param message: command
    :return: None
    """

    str_res = get_statistics_for_admin()

    await bot.reply_to(message, _wrap_as_markdown(str_res),
                       parse_mode='Markdown')


@bot.message_handler(commands=['metrics'])
async def metrics_handler(message: types.Message) -> None:
    """
    Form user statistics DataFrame and send it to user
    :param message: command
    :return: None
    """

    str_res = get_statistics_for_user(message.from_user.id)

    await bot.reply_to(message, _wrap_as_markdown(str_res),
                       parse_mode='Markdown')


@bot.message_handler(func=check_admin, commands=['new_key'])
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

    key = create_new_user_key(message.from_user.id, new_key)

    text = _join_text('Success creation', f'ID: {key.key_id}',
                      f'Name: {key.name}', 'Key in next message:')
    await bot.send_message(message.from_user.id, text)
    await bot.send_message(message.from_user.id,
                           _wrap_as_markdown(key.access_url),
                           parse_mode='Markdown')
    if message.chat.type != "private":
        await bot.reply_to(message, "Credentials sent to your DM.")


@bot.message_handler(func=check_admin, commands=['get_key'])
async def get_key_handler(message: types.Message) -> None:
    """
    Try to get credentials for existing key in OutlineVPN server
    :param message: command and new key name
    :return: None
    """
    try:
        key_id = message.text.split()[1]
    except IndexError:
        await bot.reply_to(message, "Key ID is not valid")
        return
    try:
        key = client.get_key(key_id=key_id)
    except OutlineServerErrorException:
        await bot.reply_to(message, "Unable to get key")
        return

    text = _join_text('Got key', f'ID: {key.key_id}',
                      f'Name: {key.name}', 'Key in next message:')
    await bot.send_message(message.from_user.id, text)
    await bot.send_message(message.from_user.id,
                           _wrap_as_markdown(key.access_url),
                           parse_mode='Markdown')
    if message.chat.type != "private":
        await bot.reply_to(message, "Credentials sent to your DM.")


@bot.message_handler(func=check_admin, commands=['admin_delete_key'])
async def delete_key_handler(message: types.Message) -> None:
    """
    Try to delete old key from OutlineVPN server
    :param message: command
    :return: None
    """
    markup = types.InlineKeyboardMarkup(row_width=1)

    buttons = get_admin_key_deletion_buttons()
    markup.add(*buttons)

    await bot.send_message(message.chat.id, "Choose key for deletion",
                           reply_markup=markup)


@bot.message_handler(func=check_admin, commands=['delete_key'])
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

    buttons = get_users_for_approve_buttons()
    markup.add(*buttons)

    await bot.send_message(message.chat.id, "Choose user for approve",
                           reply_markup=markup)


def check_admin_callback(call: types.CallbackQuery) -> bool:
    """
    Check if callback was sent by admin or not
    :param call: callback
    :return: True if user is admin, False otherwise
    """
    if str(call.from_user.id) not in ADMINS:
        bot.answer_callback_query(call.id, "Permission denied")
        return False
    return True


def cancel_callback(call: types.CallbackQuery) -> bool:
    """
    Check if cancel callback was sent
    :param call:
    :return: True if cancel was sent, False otherwise
    """
    if call.data != 'cancel':
        return False
    return True


@bot.callback_query_handler(
    func=lambda call: check_admin_callback(call) and cancel_callback(call))
async def callback_query_cancel_handler(call: types.CallbackQuery) -> None:
    """
    Handle pressing button for cancel action
    :param call:
    :return: None
    """
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                text='Canceled')
    await bot.answer_callback_query(call.id, "Canceled")


@bot.callback_query_handler(func=check_admin_callback)
async def callback_query_handler(call: types.CallbackQuery) -> None:
    """
    Handle pressing button for deleting key
    :param call: Pressed button
    :return: None
    """
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id

    action = call.data.split(' ')[0]
    data_id = call.data.split(' ')[1]

    if action not in CallbackEnum.__members__:
        await bot.answer_callback_query(call.id, "Action not found")

    if action == CallbackEnum.delete_key.value:
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
        approve_status_ok = approve_new_user(data_id)
        if approve_status_ok:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text=f'Success approve\nID: {data_id}')
            await bot.answer_callback_query(call.id, "Done")
        else:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text="Failed approve")
            await bot.answer_callback_query(call.id, "Failed")


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

    # todo добавить разграничение команд в зависимости от роли после start
    commands = [
        BotCommand(command='start', description='Start'),
        BotCommand(command='admin_metrics', description='Show admin statistics'),
        BotCommand(command='metrics', description='Show user statistics'),
        BotCommand(command='new_key', description='Add new key'),
        BotCommand(command='get_key',
                   description='Get credentials for existing key'),
        BotCommand(command='users_for_approve', description='Get users for approve'),
        BotCommand(command='admin_delete_key', description='Delete old key'),
        BotCommand(command='delete_key', description='Delete old key'),
        BotCommand(command='help', description='Get help')
    ]

    await bot.set_my_commands(commands=commands)

    await bot.infinity_polling()
