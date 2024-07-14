import logging

from telegram import Update, BotCommandScopeDefault, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from outline_vpn.outline_vpn import OutlineVPN
import pandas as pd
from dotenv import dotenv_values
import asyncio

config = dotenv_values(".env")

client = OutlineVPN(api_url=config['API_URL'],
                    cert_sha256=config['CERT_SHA256'],)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def wrap_as_markdown(text):
    return '```\n' + text + '\n```'

async def metrics_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    headers = ['id', 'name', 'amount(Gb)']
    client_data = pd.DataFrame(columns=headers)

    for key in client.get_keys():
        key.used_bytes = 0 if key.used_bytes is None else key.used_bytes

        used_gbytes = (key.used_bytes / 1024 / 1024 / 1024).__round__(2)
        client_data.loc[len(client_data.index)] = [key.key_id, key.name, used_gbytes]

    client_data = client_data.sort_values(by='amount(Gb)', ascending=False, ignore_index=True)

    str_res = client_data.to_markdown(index=False)

    await update.message.reply_markdown_v2(wrap_as_markdown(str_res))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Use /metrics to show VPN data info"
    )

async def new_key_callback(update, context):
    new_user = " ".join(context.args)

    key = client.create_key(
        name=new_user,
    )

    await update.message.reply_markdown_v2(
       'Success creation \n' +
       'User: ' + key.name + '\n' +
       wrap_as_markdown(key.access_url)
    )

async def delete_key_callback(update, context):
    delete_id = context.args[0]

    delete_status_ok = client.delete_key(delete_id)

    if delete_status_ok:
        await update.message.reply_text('Success deletion')
    else:
        await update.message.reply_text('Error, deletion failed')

async def start_callback(update, context):
    await update.message.reply_text('Welcome to Outline, body!')


def main():

    application = (
        Application.builder()
        .token(config['BOT_TOKEN'])
        .build()
    )

    commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='metrics', description='Получить статистику'),
                BotCommand(command='new_key', description='Добавить ключ'),
                BotCommand(command='delete_key', description='Удалить ключ'),
                BotCommand(command='help', description='Помощь')]

   # await application.bot.set_my_commands(commands, BotCommandScopeDefault())

    application.add_handler(CommandHandler("start", start_callback))
    application.add_handler(CommandHandler("metrics", metrics_callback))
    application.add_handler(CommandHandler("new_key", new_key_callback))
    application.add_handler(CommandHandler("delete_key", delete_key_callback))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()