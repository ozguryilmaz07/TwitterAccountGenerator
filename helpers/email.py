import time
import traceback
from contextlib import contextmanager
from typing import Optional, List

import tls_client

from . import exceptions


class Kopeechka:
    def __init__(self, api_key: str, accepted_domains: List[str]) -> None:
        self.api_key = api_key
        self.session = tls_client.Session(
            client_identifier="chrome_118", random_tls_extension_order=True
        )
        self.mail_types = ",".join([mail.upper() for mail in accepted_domains])

    @property
    def base_url(self) -> str:
        return "https://api.kopeechka.store"

    @property
    def base_create_mail(self) -> tuple[str, dict]:
        url = self.base_url + "/mailbox-get-email"
        params = {
            "site": "https://twitter.com/",
            "mail_type": self.mail_types,
            "token": self.api_key,
            "password": "0",
            "type": "/json",
            "api": "2.0",
        }
        return url, params

    def base_get_messages(self, activation_id: str) -> tuple[str, dict]:
        url = self.base_url + "/mailbox-get-message"
        params = {
            "id": int(activation_id),
            "token": self.api_key,
            "full": "0",
            "type": "/json",
            "api": "2.0",
        }
        return url, params

    def base_cancel_email(self, activation_id: str) -> tuple[str, dict]:
        url = self.base_url + "/mailbox-cancel"
        params = {
            "id": int(activation_id),
            "token": self.api_key,
            "type": "/json",
            "api": "2.0",
        }
        return url, params

    @contextmanager
    def rent_email(self) -> tuple[str, str]:
        id_ = 0
        try:
            url, params = self.base_create_mail
            r = self.session.get(url, params=params)
            jsn = r.json()
            if jsn["status"] != "OK":
                if jsn["status"] == "OUT_OF_STOCK":
                    return self.rent_email()
                raise exceptions.RentError(jsn["value"])
            id_ = jsn["id"]
            yield id_, jsn["mail"]
        except:
            print(traceback.format_exc())

        finally:
            self.cancel_email(id_)

    def get_code(self, activation_id: str, max_retries: Optional[int] = None) -> str:
        if not max_retries:
            max_retries = 15
        url, params = self.base_get_messages(activation_id)
        for _ in range(max_retries):
            r = self.session.get(url, params=params)
            jsn = r.json()
            if jsn["status"] != "OK":
                if jsn["value"] != "WAIT_LINK":
                    raise exceptions.GetCodeError(jsn["value"])
                time.sleep(2)
                continue
            return jsn["value"]

    def cancel_email(self, activation_id: str) -> bool:
        url, params = self.base_cancel_email(activation_id)
        r = self.session.get(url, params=params)
        jsn = r.json()
        if jsn["status"] != "OK":
            return False
        return True
