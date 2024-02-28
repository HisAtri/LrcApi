import pyaes


class Crypto:
    def __init__(self):
        self.key = self.gen_key()

    @staticmethod
    def gen_key():
        """
        生成一个32位的AES密钥
        :return: 32位随机字符串作AES密钥
        """
        import random
        import string
        aes_key: str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        return aes_key

    def encrypt(self, data: str) -> str:
        """
        加密数据，只接收JSON字符串，不负责JSON编解码
        :param data: json string
        :return: encrypted data
        """
        aes = pyaes.AESModeOfOperationCTR(self.key.encode())
        return aes.encrypt(data).hex()

    def decrypt(self, data: str) -> str:
        """
        解密数据，返回JSON字符串
        :param data: encrypted data
        :return: json string
        """
        aes = pyaes.AESModeOfOperationCTR(self.key.encode())
        return aes.decrypt(bytes.fromhex(data)).decode()

    def change_key(self):
        self.key = self.gen_key()


crypto = Crypto()
