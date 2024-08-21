import pandas as pd
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.types import BotCommand

from config import ADMINS, BOT_TOKEN
from exceptions import BotExceptionHandler, OutlineServerErrorException
from outline import get_outline_client
from utils import _join_text, _wrap_as_markdown

bot = AsyncTeleBot(BOT_TOKEN,
                   exception_handler=BotExceptionHandler())
client = get_outline_client()


@bot.message_handler(commands=['start'])
async def start_handler(message: types.Message) -> None:
    """
    Show greeting to user
    :param message: command
    :return: None
    """
    await bot.reply_to(message, 'Welcome to Outline, body!')


@bot.message_handler(commands=['metrics'])
async def metrics_handler(message: types.Message) -> None:
    """
    Form statistics DataFrame and send it to user
    :param message: command
    :return: None
    """
    data = {'ID': [], 'Name': [], 'GB': []}

    for key in client.get_keys():
        key.used_bytes = 0 if key.used_bytes is None else key.used_bytes

        used_gbytes = round(key.used_bytes / 1024 / 1024 / 1024, 2)
        data['ID'].append(key.key_id)
        data['Name'].append(key.name)
        data['GB'].append(used_gbytes)

    client_data = pd.DataFrame(data=data).sort_values(by='GB',
                                                      ascending=False,
                                                      ignore_index=True)

    str_res = client_data.to_markdown(index=False)

    await bot.reply_to(message, _wrap_as_markdown(str_res),
                       parse_mode='Markdown')


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


@bot.message_handler(func=check_admin, commands=['new_key'])
async def new_key_handler(message: types.Message) -> None:
    """
    Try to create a new key in OutlineVPN server
    :param message: command and new key name
    :return: None
    """
    try:
        new_user = message.text.split()[1]
    except IndexError:
        await bot.reply_to(message, "Key name is not valid")
        return

    try:
        await bot.send_message(message.from_user.id, 'Hi!')
    except Exception:
        await bot.reply_to(message, "Make sure bot has access to message you.")
        return

    key = client.create_key(
        name=new_user,
    )

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
        await bot.send_message(message.from_user.id, 'Hi!')
    except Exception:
        await bot.reply_to(message, "Make sure bot has access to message you.")
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


@bot.message_handler(func=check_admin, commands=['delete_key'])
async def delete_key_handler(message: types.Message) -> None:
    """
    Try to delete old key from OutlineVPN server
    :param message: command
    :return: None
    """
    markup = types.InlineKeyboardMarkup(row_width=1)

    keys = client.get_keys()

    buttons = []
    for key in keys:
        button = types.InlineKeyboardButton(
            f"ID: {key.key_id}, Name: {key.name}",
            callback_data=key.key_id)
        buttons.append(button)

    cancel_button = types.InlineKeyboardButton("Cancel",
                                               callback_data='cancel')
    buttons.append(cancel_button)
    markup.add(*buttons)

    await bot.send_message(message.chat.id, "Choose key for deletion",
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

    delete_status_ok = client.delete_key(call.data)

    if delete_status_ok:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text=f'Success deletion\nID: {call.data}')
        await bot.answer_callback_query(call.id, "Done")
    else:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                    text="Failed deletion")
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
    commands = [
        BotCommand(command='start', description='Start'),
        BotCommand(command='metrics', description='Show statistics'),
        BotCommand(command='new_key', description='Add new key'),
        BotCommand(command='get_key',
                   description='Get credentials for existing key'),
        BotCommand(command='delete_key', description='Delete old key'),
        BotCommand(command='help', description='Get help')
    ]

    await bot.set_my_commands(commands=commands)

    await bot.infinity_polling()
