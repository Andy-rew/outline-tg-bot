import pandas as pd
from outline_vpn.outline_vpn import OutlineKey


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
