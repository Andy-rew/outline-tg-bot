
class Key:

    def __init__(self, key_id, name, used_bytes, access_url):
        self.key_id = int(key_id)
        self.name = name
        self.used_bytes = used_bytes
        self.access_url = access_url


class OutlineMockService:
    all_keys = []

    def __init__(self):
        keys = []

        for i in range(10):
            key = Key(i, 'aboba_' + str(i), 13118344154 + 1000000000 * i, 'https://www.google.com')
            keys.append(key)

        self.all_keys = keys

    def create_key(self, name):
        len_keys = len(self.all_keys)

        key = Key(len_keys, name, 0, "https://www.google.com")

        self.all_keys.append(key)

        return key

    def delete_key(self, key_id):
        self.all_keys = [key for key in self.all_keys if key.key_id != key_id]
        return True

    def get_keys(self):
        return self.all_keys
