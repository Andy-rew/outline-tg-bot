from outline_vpn.outline_vpn import OutlineKey

from db_models import get_user_keys
from utils import create_statistic_md_table


def get_statistics_for_admin(keys: list[OutlineKey]):
    return create_statistic_md_table(keys)


def get_statistics_for_user(tg_id, keys: list[OutlineKey]):
    user_keys = get_user_keys(tg_id)
    keys_for_user = [key for key in keys if key.key_id in [key.key_id for key in user_keys]]
    return create_statistic_md_table(keys_for_user)
