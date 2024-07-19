import asyncio

import pandas as pd
from dotenv import dotenv_values
from outline_vpn.outline_vpn import OutlineVPN
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.types import BotCommand

config = dotenv_values(".env")

bot = AsyncTeleBot(config['BOT_TOKEN'])

client = OutlineVPN(api_url=config['API_URL'],
                    cert_sha256=config['CERT_SHA256'], )

admins = config['ADMINS'].split(',')


def wrap_as_markdown(text: str) -> str:
    return f'```\n{text}\n```'


@bot.message_handler(commands=['metrics'])
async def metrics_callback(message: types.Message) -> None:
    data = {'id': [], 'name': [], 'amount(Gb)': []}

    for key in client.get_keys():
        key.used_bytes = 0 if key.used_bytes is None else key.used_bytes

        used_gbytes = round(key.used_bytes / 1024 / 1024 / 1024, 2)
        data['id'].append(key.key_id)
        data['name'].append(key.name)
        data['amount(Gb)'].append(used_gbytes)

    client_data = pd.DataFrame(data=data).sort_values(by='amount(Gb)', ascending=False, ignore_index=True)

    str_res = client_data.to_markdown(index=False)

    await bot.reply_to(message, wrap_as_markdown(str_res), parse_mode='Markdown')


@bot.message_handler(commands=['help'])
async def help_command(message: types.Message) -> None:
    await bot.reply_to(message, "God will help you")


async def check_admin(message: types.Message) -> bool:
    if message.from_user.username not in admins:
        await bot.reply_to(message, "Permission denied")
        return False
    return True


@bot.message_handler(func=check_admin, commands=['new_key'])
async def new_key_callback(message: types.Message) -> None:
    try:
        new_user = message.text.split()[1]
    except IndexError:
        await bot.reply_to(message, "Key name is not valid")
        return

    key = client.create_key(
        name=new_user,
    )

    await bot.reply_to(message,
                       f'Success creation\nID: {key.key_id}\nName: {key.name}\n{wrap_as_markdown(key.access_url)}',
                       parse_mode='Markdown',
                       )


@bot.message_handler(func=check_admin, commands=['delete_key'])
async def delete_key_buttons(message: types.Message) -> None:
    markup = types.InlineKeyboardMarkup(row_width=1)

    keys = client.get_keys()

    buttons = []
    for key in keys:
        button = types.InlineKeyboardButton(f"ID: {key.key_id}, Name: {key.name}", callback_data=key.key_id)
        buttons.append(button)

    markup.add(*buttons)

    await bot.send_message(message.chat.id, "Выберите ключ для удаления", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call: types.CallbackQuery) -> None:
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id

    delete_status_ok = client.delete_key(call.data)
    if delete_status_ok:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'Success deletion\nID: {call.data}')
        await bot.answer_callback_query(call.id, "Готово")
    else:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Failed deletion")
        await bot.answer_callback_query(call.id, "Провал")


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

    await bot.polling()


if __name__ == '__main__':
    asyncio.run(main())
