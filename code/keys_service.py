from outline_vpn.outline_vpn import OutlineKey
from telebot import types

from code.db_models import get_users_for_approve, create_new_key, get_user_by_tg_id
from code.exceptions import AbobaError, OutlineServerErrorException
from code.outline import get_outline_client
from code.user_service import filter_user_keys
from code.utils import create_keys_list_buttons, create_users_list_buttons, CallbackEnum

client = get_outline_client()


def get_admin_key_deletion_buttons(tg_id) -> list[types.InlineKeyboardButton]:
    keys = client.get_keys()
    return create_keys_list_buttons(keys, tg_id, CallbackEnum.delete_key.value)


def get_user_key_deletion_buttons(tg_id) -> list[types.InlineKeyboardButton]:
    keys = client.get_keys()
    keys_for_user = filter_user_keys(keys, tg_id)
    return create_keys_list_buttons(keys_for_user, tg_id,
                                    CallbackEnum.delete_key.value)


def delete_key(key_id) -> bool:
    return client.delete_key(key_id)


def get_users_for_approve_buttons(tg_id) -> list[types.InlineKeyboardButton]:
    users = get_users_for_approve()
    return create_users_list_buttons(users, tg_id)


def create_new_user_key(tg_id, name):
    user = get_user_by_tg_id(tg_id)

    if not user:
        raise AbobaError('User not found')

    if user.is_approved is False:
        raise AbobaError(
            'You are not approved. Please wait for admin approval')

    if len(user.keys) == user.keys_count:
        raise AbobaError('Max keys count reached')

    key = client.create_key(
        name=name,
    )
    create_new_key(user, name, key.key_id)
    return key


def get_key_info(tg_id, key_id) -> OutlineKey:
    user = get_user_by_tg_id(tg_id)

    if not user:
        raise AbobaError('User not found')

    if user.is_approved is False:
        raise AbobaError(
            'You are not approved. Please wait for admin approval')

    if key_id not in [key.key_id for key in user.keys]:
        raise AbobaError(f'Key with id={key_id}  not found')

    try:
        key = client.get_key(key_id=key_id)
    except OutlineServerErrorException:
        raise AbobaError("Unable to get key")

    return key


def get_user_key_view_buttons(tg_id) -> list[types.InlineKeyboardButton]:
    keys = client.get_keys()
    keys_for_user = filter_user_keys(keys, tg_id)
    return create_keys_list_buttons(keys_for_user, tg_id,
                                    CallbackEnum.view_key.value)
