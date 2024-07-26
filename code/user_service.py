from db_models import create_new_user_on_start, get_user


def new_user_start(tg_id, name):
    exist_user = get_user(tg_id)

    if exist_user and exist_user.is_approved is True:
        # todo ошибка и сообщение что юзер есть и апрувнут, может юзать бота
        return

    if exist_user and exist_user.is_approved is False:
        # todo ошибка и сообщение что юзер есть и не апрувнут пусть ждет апрува
        return

    create_new_user_on_start(tg_id, name)
