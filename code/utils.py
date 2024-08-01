from enum import Enum

import pandas as pd
from outline_vpn.outline_vpn import OutlineKey
from telebot import types

from db_models import Users


class CallbackEnum(Enum):
    delete_key = 'delete_key'
    approve_user = 'approve_user'
    cancel = 'cancel',
    view_key = 'view_key'


def _wrap_as_markdown(text: str) -> str:
    """
    Wrap input text into triple single quotes
    :param text: input text
    :return: wrapped text
    """
    return f'```\n{text}\n```'


def _join_text(*texts: str) -> str:
    """
    Join input strings into one string separated by a line break
    :param texts: input strings
    :return: joined string
    """
    return '\n'.join(texts)


def create_statistic_md_table(keys: list[OutlineKey]):
    data = {'ID': [], 'Name': [], 'GB': []}

    for key in keys:
        key.used_bytes = 0 if key.used_bytes is None else key.used_bytes

        used_gbytes = round(key.used_bytes / 1024 / 1024 / 1024, 2)
        data['ID'].append(key.key_id)
        data['Name'].append(key.name)
        data['GB'].append(used_gbytes)

    client_data = pd.DataFrame(data=data).sort_values(by='GB',
                                                      ascending=False,
                                                      ignore_index=True)

    str_res = client_data.to_markdown(index=False)
    return str_res


def create_keys_list_buttons(keys: list[OutlineKey], tg_id, callback_type) -> list[types.InlineKeyboardButton]:
    buttons = []
    for key in keys:
        button = types.InlineKeyboardButton(
            f"ID: {key.key_id}, Name: {key.name}",
            callback_data=f"{callback_type} {tg_id} {key.key_id}")
        buttons.append(button)

    cancel_button = types.InlineKeyboardButton("Cancel",
                                               callback_data=f'{callback_type} {tg_id}')
    buttons.append(cancel_button)
    return buttons


def create_users_list_buttons(users: list[Users], tg_id) -> list[types.InlineKeyboardButton]:
    buttons = []
    for user in users:
        button = types.InlineKeyboardButton(
            f"ID: {user.id}, Name: {user.name}",
            callback_data=f"{CallbackEnum.approve_user.value} {tg_id} {user.id}")
        buttons.append(button)

    cancel_button = types.InlineKeyboardButton("Cancel",
                                               callback_data=f'{CallbackEnum.cancel.value} {tg_id}')
    buttons.append(cancel_button)
    return buttons
