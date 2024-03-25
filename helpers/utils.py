import base64
import json
import os
import random
import secrets
import uuid
from ssl import SSLContext
from typing import Dict, List, Tuple

from attr import dataclass
from httpx import create_ssl_context


@dataclass
class Config:
    threads: int
    capsolver_key: str
    yescaptcha_key: str
    allowed_captcha_solvers: List[str]
    kopeechka_key: str
    account_password: str
    accepted_email_domains: List[str]
    use_pfp: bool
    use_username: bool


with open("data/config.json", "r", encoding="utf-8") as config_file:
    config = json.load(config_file)
    config = Config(**config)

with open("data/proxies.txt", "r", encoding="utf-8") as file:
    proxies = file.read().splitlines()

pfps = os.listdir("data/pfps")

with open("data/usernames.txt", "r", encoding="utf-8") as file:
    usernames = file.read().splitlines()


def fill_remaining_chars(s: str) -> str:
    remaining_chars = 15 - len(s)
    if remaining_chars > 0:
        if random.choice([True, False]):
            return s + secrets.token_hex(remaining_chars // 2)
        return s + str(random.randint(0, 9)) * (remaining_chars // 2)
    return s


def get_random_username() -> str:
    return fill_remaining_chars(random.choice(usernames))


def get_random_pfp() -> str:
    with open("data/pfps" + "/" + random.choice(pfps), "rb") as pic:
        return base64.b64encode(pic.read()).decode("utf-8")


def random_pfp_fiile() -> str:
    return "data/pfps" + "/" + random.choice(pfps)


def get_random_proxies() -> Dict[str, str]:
    proxy = random.choice(proxies)
    proxy_dict = {"all://": f"http://{proxy}"}
    return proxy_dict


def get_uuid() -> str:
    return str(uuid.uuid4()).replace("-", "")


def get_context() -> SSLContext:
    context = create_ssl_context()
    cipher1 = "ECDH+AESGCM:ECDH+CHACHA20:DH+AESGCM:DH+CHACHA20:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:DH+HIGH:RSA+AESGCM:RSA+AES:RSA+HIGH"

    context.set_alpn_protocols(["h2"])
    context.set_ciphers(cipher1)

    return context


def birthdate() -> Tuple[int, int, int]:  # day, month, year
    return random.randint(1, 28), random.randint(1, 12), random.randint(1970, 1999)
