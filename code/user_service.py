from outline_vpn.outline_vpn import OutlineKey

from db_models import create_new_user_on_start, get_user_keys, approve_user, get_user_by_id, get_user_by_tg_id


def filter_user_keys(keys: list[OutlineKey], tg_id):
    user_keys = get_user_keys(tg_id)
    keys_for_user = [key for key in keys if key.key_id in [key.key_id for key in user_keys]]
    return keys_for_user


def new_user_start(tg_id, name):
    exist_user = get_user_by_tg_id(tg_id)

    if exist_user and exist_user.is_approved is True:
        # todo ошибка и сообщение что юзер есть и апрувнут, может юзать бота
        return

    if exist_user and exist_user.is_approved is False:
        # todo ошибка и сообщение что юзер есть и не апрувнут пусть ждет апрува
        return

    create_new_user_on_start(tg_id, name)


def approve_new_user(user_id) -> bool:
    approve_user(user_id)
    user = get_user_by_id(user_id)
    return user.is_approved
