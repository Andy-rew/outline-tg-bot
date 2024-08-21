from code.outline import get_outline_client
from code.user_service import filter_user_keys
from code.utils import create_statistic_md_table
from run import client


def get_statistics_for_admin():
    keys = client.get_keys()
    return create_statistic_md_table(keys)


def get_statistics_for_user(tg_id):
    keys = client.get_keys()
    keys_for_user = filter_user_keys(keys, tg_id)
    return create_statistic_md_table(keys_for_user)
