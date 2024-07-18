
from telegram import Update, BotCommand
from telegram.constants import ParseMode
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from telebot.types import BotCommand

from outline_vpn.outline_vpn import OutlineVPN
import pandas as pd
from dotenv import dotenv_values
import asyncio

config = dotenv_values(".env")

bot = AsyncTeleBot(config['BOT_TOKEN'])

client = OutlineVPN(api_url=config['API_URL'],
                    cert_sha256=config['CERT_SHA256'], )

admins = config['ADMINS'].split(',')


def wrap_as_markdown(text):
    return '```\n' + text + '\n```'


@bot.message_handler(commands=['metrics'])
async def metrics_callback(message: types.Message) -> None:
    headers = ['id', 'name', 'amount(Gb)']
    client_data = pd.DataFrame(columns=headers)

    for key in client.get_keys():
        key.used_bytes = 0 if key.used_bytes is None else key.used_bytes

        used_gbytes = (key.used_bytes / 1024 / 1024 / 1024).__round__(2)
        client_data.loc[len(client_data.index)] = [key.key_id, key.name, used_gbytes]

    client_data = client_data.sort_values(by='amount(Gb)', ascending=False, ignore_index=True)

    str_res = client_data.to_markdown(index=False)

    await bot.reply_to(message, wrap_as_markdown(str_res), parse_mode=ParseMode.MARKDOWN)


@bot.message_handler(commands=['help'])
async def help_command(message: types.Message) -> None:
    await bot.reply_to(message, "God will help you")


@bot.message_handler(commands=['new_key'])
async def new_key_callback(message: types.Message) -> None:

    if message.from_user.username not in admins:
        await bot.reply_to(message, "Only admins can create keys")
        return

    try:
        new_user = message.text.split()[1]
    except Exception:
        await bot.reply_to(message, "Key name is not valid")

    key = client.create_key(
        name=new_user,
    )

    await bot.reply_to(message,
                       'Success creation \n' +
                       'User: ' + key.name + '\n' +
                       wrap_as_markdown(key.access_url),
                       parse_mode=ParseMode.MARKDOWN
                       )


@bot.message_handler(commands=['delete_key'])
async def delete_key_callback(message: types.Message) -> None:

    if message.from_user.username not in admins:
        await bot.reply_to(message, "Only admins can delete keys")
        return

    try:
        delete_id = message.text.split()[1]
    except Exception:
        await bot.reply_to(message, "Key id is not valid")

    delete_status_ok = client.delete_key(delete_id)

    if delete_status_ok:
        await bot.reply_to(message, 'Success deletion')
    else:
        await bot.reply_to(message, 'Error, deletion failed')


@bot.message_handler(commands=['start'])
async def start_callback(message: types.Message) -> None:
    await bot.reply_to(message, 'Welcome to Outline, body!')


async def main():
    commands = [
        BotCommand(command='start', description='Старт'),
        BotCommand(command='metrics', description='Получить статистику'),
        BotCommand(command='new_key', description='Добавить ключ'),
        BotCommand(command='delete_key', description='Удалить ключ'),
        BotCommand(command='help', description='Помощь')
    ]

    await bot.set_my_commands(commands=commands)

    await bot.polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    asyncio.run(main())
