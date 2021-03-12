# -*- encoding=utf-8 -*-


from .cryption import Cryption


class Phone(object):

    @classmethod
    def encrypt(cls, number: str, fixed:bool=True) -> str:
        """
        加密手机号
        :param number: 手机号
        :return: 加密后手机号
        """
        return Cryption.encrypt(data=number, fixed=fixed)

    @classmethod
    def decrypt(cls, encrypt_str: str, fixed:bool=True) -> str:
        """
        解密手机号
        :param cryption_str: 加密字符串
        :return: 解密后的手机号
        """
        return Cryption.decrypt(data=encrypt_str, fixed=fixed)

    @classmethod
    def encryption_phone(cls, encrypt_str:str, fixed:bool=True) -> str:
        """脱敏手机号"""
        decrypt_phone = cls.decrypt(encrypt_str, fixed=fixed)
        head = decrypt_phone[0: 3]
        tail = decrypt_phone[7: 12]
        phone = head + '****' + tail
        return phone

    @classmethod
    def encryption_card(cls, encrypt_str: str) -> str:
        """脱敏身份证号"""
        card = ''
        if encrypt_str:
            encrypt_str = cls.decrypt(encrypt_str,fixed=True)
            # card = encrypt_str.replace(encrypt_str[7:12],'******')
            if len(encrypt_str) >= 16:
                card = encrypt_str.replace(encrypt_str[int((round(len(encrypt_str) / 2, 0) - 4)):int((round(len(encrypt_str) / 2, 0) + 4))], '********')
            elif len(encrypt_str) >= 10:
                card = encrypt_str.replace(encrypt_str[int((round(len(encrypt_str) / 2, 0) - 3)):int((round(len(encrypt_str) / 2, 0) + 3))], '******')
            else:
                if len(encrypt_str) > 5:
                    card = encrypt_str.replace(encrypt_str[int((round(len(encrypt_str) / 2, 0) - 2)):int((round(len(encrypt_str) / 2, 0) + 2))], '****')
                else:
                    card = encrypt_str.replace(encrypt_str[int((round(len(encrypt_str) / 2, 0) - 1)):int((round(len(encrypt_str) / 2, 0) + 1))], '**')
        return card
