from outline_vpn.outline_vpn import OutlineKey


class OutlineMockService:
    all_keys = []

    def __init__(self):
        keys = []
        for i in range(10):
            key = OutlineKey({})
            key.key_id = f'{i}'
            key.name = f'aboba_{i}'
            key.used_bytes = 13118344154 + 1000000000 * i
            key.access_url = 'https://www.google.com'

            keys.append(key)

        self.all_keys = keys

    def create_key(self, name):
        len_keys = len(self.all_keys)

        key = OutlineKey({})
        key.key_id = len_keys
        key.name = name
        key.used_bytes = None
        key.access_url = 'https://www.google.com'

        self.all_keys.append(key)

        return key

    def delete_key(self, key_id):
        self.all_keys = [key for key in self.all_keys if key.key_id != key_id]
        return True

    def get_keys(self):
        return self.all_keys
