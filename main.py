
# Create a new key
# new_key = client.create_key()
#
# # Or create a key with a specific attributes
# key = client.create_key(
#     key_id="new_key_001",
#     name="Yet another test key",
#     data_limit=1024 * 1024 * 20,
#     method="aes-192-gcm",
#     password="test",
#     port=2323,
# )

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from outline_vpn.outline_vpn import OutlineVPN
import pandas as pd
from dotenv import dotenv_values

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    headers = ['name', 'amount(Gb)']
    client_data = pd.DataFrame(columns=headers)
    client_data_arr = []
    # Get all access URLs on the server
    for key in client.get_keys():
        if key.used_bytes:
            used_gbytes = (key.used_bytes / 1024 / 1024 / 1024).__round__(2)
            client_data.loc[len(client_data.index)] = [key.name, used_gbytes]
            client_data_arr.append([key.name, used_gbytes])

    client_data = client_data.sort_values(by='amount(Gb)', ascending=False, ignore_index=True)

    str_res = client_data.to_markdown(index=False)

    await update.message.reply_markdown_v2('```\n' + str_res + '\n```')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text(
        "Use /start to show VPN data info"
    )

def main() -> None:

    application = (
        Application.builder()
        .token(config['BOT_TOKEN'])
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
