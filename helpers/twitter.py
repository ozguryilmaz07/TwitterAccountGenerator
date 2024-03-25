import ctypes
import hashlib
import secrets
import string
from os import path
from typing import List, Dict, Optional
from uuid import uuid4

import requests
from httpx import Client

from . import utils

LIBRARY = ctypes.CDLL("helpers/instrumentation.so")

class SessionManager:
    def __init__(self, proxies: List[str]) -> None:
        self.proxies = proxies

    @property
    def account_statuses(self) -> Dict[str, str]:
        return {
            "https://twitter.com/account/access": "LOCKED",
            "/i/flow/consent_flow": "CONSENT",
            "is suspended and": "SUSPENDED",
            "not authenticate you": "DELETED",
        }

    def check_token(self, token: str) -> str:
        session = self.init_session(token)
        check = session.post(
            "https://twitter.com/i/api/1.1/account/update_profile.json"
        )
        if check.status_code == 200:
            return "UNLOCKED"
        status = "UNKNOWN"
        for key, value in self.account_statuses.items():
            if key in check.text:
                status = value
        return status

    def init_session(self, token: str) -> Client:
        session = Client(
            proxies=utils.get_random_proxies(),
            timeout=30
        )
        session.cookies["auth_token"] = token
        self._get_cookies(session)
        return session

    def _get_cookies(self, session: Client) -> None:
        try:
            session.headers = {
                "authority": "twitter.com",
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.7",
                "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
                "content-type": "application/json",
                "referer": "https://twitter.com/",
                "sec-ch-ua": '"Not/A)Brand";v="99", "Brave";v="120", "Chromium";v="120"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "sec-gpc": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "x-client-transaction-id": "k5EGS2Mu/OnX/xGtwHtqbZ8/euSDYZUWpn/44FpzElhoSbuNTCnfFpcK+ajyPP/491pZHpMbTSnGQtiP7O5YuwjO74Hikg",
                "x-client-uuid": str(uuid4()),
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "en",
            }
            session.post(
                "https://twitter.com/i/api/1.1/account/update_profile.json"
            )
            session.headers["x-csrf-token"] = session.cookies.get("ct0")
        except TimeoutError:
            return

    @staticmethod
    def get_file_size(file: str) -> Optional[str]:
        try:
            return str(path.getsize(file))
        except FileNotFoundError:
            print(f"Error: File '{file}' not found.")
            return None

    @staticmethod
    def calculate_md5(file_path: str):
        md5_hash = hashlib.md5()

        with open(file_path, "rb") as file:
            for byte_block in iter(lambda: file.read(4096), b""):
                md5_hash.update(byte_block)

        return md5_hash.hexdigest()

    def _init_upload(self, session: Client, size: str) -> str:
        params = {
            "command": "INIT",
            "total_bytes": size,
            "media_type": "image/jpeg",
            "media_category": "tweet_image",
        }

        response = session.post(
            "https://upload.twitter.com/i/media/upload.json",
            params=params,
        )
        if response.status_code == 202:
            return response.json()["media_id"]

    def _first_append(self, session: Client, media_id: str) -> bool:
        headers = {
            "authority": "upload.twitter.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "access-control-request-headers": "authorization,x-csrf-token,x-twitter-auth-type",
            "access-control-request-method": "POST",
            "origin": "https://twitter.com",
            "referer": "https://twitter.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        params = {
            "command": "APPEND",
            "media_id": media_id,
            "segment_index": "0",
        }
        response = session.options(
            "https://upload.twitter.com/i/media/upload.json",
            params=params,
            headers=headers,
        )
        return response.status_code == 200

    def _upload_content(self, session: Client, media_id: str, file: str) -> bool:
        params = {
            "command": "APPEND",
            "media_id": media_id,
            "segment_index": "0",
        }
        headers = {
            "authority": "upload.twitter.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.6",
            "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
            "origin": "https://twitter.com",
            "referer": "https://twitter.com/",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "x-csrf-token": session.headers["x-csrf-token"],
            "x-twitter-auth-type": "OAuth2Session",
        }

        if not file.startswith("http"):
            with open(file, "rb") as f:
                file_content = f.read()
        else:
            file_content = requests.get(file).content

        response = requests.post(
            "https://upload.twitter.com/i/media/upload.json",
            params=params,
            files={"media": file_content},
            cookies=session.cookies,
            headers=headers,
        )
        return response.status_code == 204

    def _finalize(
        self, session: Client, media_id: str, file_hash: Optional[str] = None
    ) -> str:
        headers = {
            "authority": "upload.twitter.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "access-control-request-headers": "authorization,x-csrf-token,x-twitter-auth-type",
            "access-control-request-method": "POST",
            "origin": "https://twitter.com",
            "referer": "https://twitter.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        params = {
            "command": "FINALIZE",
            "media_id": media_id,
        }
        if file_hash:
            params["original_md5"] = file_hash
        first = session.options(
            "https://upload.twitter.com/i/media/upload.json",
            params=params,
            headers=headers,
        )
        if first.status_code == 200:
            response = session.post(
                "https://upload.twitter.com/i/media/upload.json", params=params
            )
            if response.status_code == 201:
                return response.json()["media_id_string"]

    def upload(
        self, session: Client, file: str, confirm_hash: Optional[bool] = None
    ) -> Optional[str]:
        if not confirm_hash:
            file_hash = None
        else:
            file_hash = self.calculate_md5(file)
        if file.startswith("http"):
            r = requests.post(file)
            size = len(r.content)
        else:
            size = self.get_file_size(file)
        media_id = self._init_upload(session, size)
        if media_id is None:
            return "no_media_id"
        appended = self._first_append(session, media_id)
        if not appended:
            return "no_append"
        uploaded = self._upload_content(session, media_id, file)
        if not uploaded:
            return "no_upload"
        return self._finalize(session, media_id, file_hash=file_hash)

    def set_pfp(self, session: Client, filename: str) -> bool:
        media_id = self.upload(session=session, file=filename, confirm_hash=True)
        if not media_id:
            return False
        headers = {
            **session.headers,
            "content-type": "application/x-www-form-urlencoded",
            "x-csrf-token": session.cookies["ct0"],
        }
        data = {
            "include_profile_interstitial_type": "1",
            "include_blocking": "1",
            "include_blocked_by": "1",
            "include_followed_by": "1",
            "include_want_retweets": "1",
            "include_mute_edge": "1",
            "include_can_dm": "1",
            "include_can_media_tag": "1",
            "include_ext_has_nft_avatar": "1",
            "include_ext_is_blue_verified": "1",
            "include_ext_verified_type": "1",
            "include_ext_profile_image_shape": "1",
            "skip_status": "1",
            "return_user": "true",
            "media_id": media_id,
        }
        response = session.post(
            "https://api.twitter.com/1.1/account/update_profile_image.json",
            headers=headers,
            data=data,
        )
        return response.status_code == 200



def solve_instrumentation(data: str) -> str:
    LIBRARY.parseScript.argtypes = [ctypes.c_char_p]
    LIBRARY.parseScript.restype = ctypes.c_char_p

    data = data.encode("utf-8")
    response = LIBRARY.parseScript(data)
    return response.decode()

def get_web_instrumentation() -> str:
    session = requests.Session()
    data = session.get(
        'https://twitter.com/i/js_inst?c_name=ui_metrics',
        headers={
            "accept": "*/*",
            "Referer": "https://twitter.com/i/flow/signup",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-origin"
        }
    )

    return solve_instrumentation(data.text)


def device_token() ->str:
    return "".join(
        secrets.choice(string.digits + string.ascii_lowercase + string.ascii_uppercase)
        for _ in range(40)
    )


def trace_id() -> str:
    return "".join(
        secrets.choice(string.digits + string.digits + string.ascii_lowercase)
        for _ in range(16)
    )
