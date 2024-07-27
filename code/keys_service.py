from telebot import types

from db_models import get_users_for_approve, create_new_key, get_user_by_tg_id
from user_service import filter_user_keys
from utils import create_deletion_keys_buttons, create_users_list_buttons
from outline import get_outline_client

client = get_outline_client()


def get_admin_key_deletion_buttons() -> list[types.InlineKeyboardButton]:
    keys = client.get_keys()
    return create_deletion_keys_buttons(keys)


def get_user_key_deletion_buttons(tg_id) -> list[types.InlineKeyboardButton]:
    keys = client.get_keys()
    keys_for_user = filter_user_keys(keys, tg_id)
    return create_deletion_keys_buttons(keys_for_user)


def delete_key(key_id) -> bool:
    return client.delete_key(key_id)


def get_users_for_approve_buttons() -> list[types.InlineKeyboardButton]:
    users = get_users_for_approve()
    return create_users_list_buttons(users)


def create_new_user_key(tg_id, name):
    user = get_user_by_tg_id(tg_id)
    # todo проверка на количество ключей

    # todo проверка на то что апрувнут

    key = client.create_key(
        name=name,
    )
    create_new_key(tg_id, name, key.key_id)
    return key
