from outline_vpn.outline_vpn import OutlineKey

from db_models import create_new_user_on_start, get_user_keys, approve_user, \
    get_user_by_id, get_user_by_tg_id, Users
from exceptions import AbobaError


def filter_user_keys(keys: list[OutlineKey], tg_id):
    user_keys = get_user_keys(tg_id)
    keys_for_user = [key for key in keys if
                     key.key_id in [key.key_id for key in user_keys]]
    return keys_for_user


def new_user_start(tg_id, name):
    exist_user = get_user_by_tg_id(tg_id)

    if exist_user and exist_user.is_approved is True:
        raise AbobaError(
            'You are already exist and approved. Print /help to get more info')

    if exist_user and exist_user.is_approved is False:
        raise AbobaError(
            'You are not approved. Please wait for admin approval')

    create_new_user_on_start(tg_id, name)


def approve_new_user(user_id) -> Users:
    approve_user(user_id)
    user = get_user_by_id(user_id)
    return user
