
import base64
import os
import logging

from Crypto import PublicKey
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5

key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public.pem")
public_key = open(key_path,"r").read()

def pwd_encrypt(pwd: str) -> str:
    """Generate encrypted password using RSA, with given public key.

    Args:
        public_key (str): given public key
        pwd (str): user's password

    Returns:
        str: encrypted password with base64 encode.
    """
    if not isinstance(public_key, str) or not isinstance(pwd, str):
        logging.error("[Type Error]:public_key and pwd must be string")
    key = RSA.importKey(public_key)
    cipher = Cipher_pkcs1_v1_5.new(key)  # 生成对象
    cipher_text = base64.b64encode(cipher.encrypt(pwd.encode(encoding="utf-8")))
    encrypted_pwd = cipher_text.decode('utf8')  # 将密文由bytes类型解码成str类型
    return encrypted_pwd

if __name__ == '__main__':
    logging.info(public_key)
    pwd = "shu"
    encrypted_pwd = pwd_encrypt(public_key, pwd)
    logging.info(encrypted_pwd)
