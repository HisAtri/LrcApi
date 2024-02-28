import pyaes


class Crypto:
    def __init__(self):
        self.key = self.gen_key()

    @staticmethod
    def gen_key():
        import random
        import string
        aes_key: str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        return aes_key

    def encrypt(self, data: str) -> str:
        aes = pyaes.AESModeOfOperationCTR(self.key.encode())
        return aes.encrypt(data).hex()

    def decrypt(self, data: str) -> str:
        aes = pyaes.AESModeOfOperationCTR(self.key.encode())
        return aes.decrypt(bytes.fromhex(data)).decode()

    def change_key(self):
        self.key = self.gen_key()


crypto = Crypto()
