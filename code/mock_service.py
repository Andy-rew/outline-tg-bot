import random

from outline_vpn.outline_vpn import OutlineKey

from config import IS_MOCK_OUTLINE, RECREATE_DB_ON_START
from db_models import create_new_user_on_start, clear_db, get_keys
from exceptions import OutlineServerErrorException


class OutlineMockService:
    all_keys = []

    def __init__(self):
        clear_db()
        create_in_db = IS_MOCK_OUTLINE is True and RECREATE_DB_ON_START is True

        if create_in_db:
            for i in range(10):
                key = OutlineKey(response={'id': str(i), 'name': f'aboba{i}',
                                           'accessUrl': 'https://www.google' +
                                                        '.com'},
                                 metrics={'bytesTransferredByUserId': {
                                     str(i): 13118344154 + 1000000000 * i}})

                self.all_keys.append(key)
                create_new_user_on_start(f'123{i * random.randint(1, 100000)}',
                                         f'aboba{i}')
        else:
            db_keys = get_keys()
            for db_key in db_keys:
                key = OutlineKey(response={'id': db_key.key_id,
                                           'name': f'{db_key.key_name}',
                                           'accessUrl': 'https://www.google' +
                                                        '.com'},
                                 metrics={'bytesTransferredByUserId': {
                                     db_key.key_id: 0}})

                self.all_keys.append(key)

    def create_key(self, name: str):
        len_keys = len(self.all_keys)

        key = OutlineKey(response={'id': str(len_keys), 'name': name,
                                   'accessUrl': 'https://www.google.com'},
                         metrics={'bytesTransferredByUserId': {
                             len_keys: None}})

        self.all_keys.append(key)

        return key

    def get_key(self, key_id: str):
        for key in self.all_keys:
            if key.key_id == key_id:
                return key
        raise OutlineServerErrorException("Unable to get key")

    def delete_key(self, key_id: str):
        self.all_keys = [key for key in self.all_keys if key.key_id != key_id]
        return True

    def get_keys(self):
        return self.all_keys
