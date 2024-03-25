import os
import random
import uuid
from logging import Logger
from threading import Lock, Thread
from typing import Final, Dict

import httpx
from faker import Faker

import exceptions
import helpers

FAKE: Final[Faker] = Faker()

solvers = {
    "capsolver": (helpers.captcha.Capsolver, helpers.utils.config.capsolver_key),
    "yescaptcha": (helpers.captcha.Yescaptcha, helpers.utils.config.yescaptcha_key),
}

ENABLED_SOLVERS = [
    solvers[solver.lower()][0](solvers[solver.lower()][1])
    for solver in helpers.utils.config.allowed_captcha_solvers
    if solver.lower() in solvers
]

assert (
    ENABLED_SOLVERS
), "Please enable at least 1 captcha solver"

LOGGER: Final[Logger] = helpers.logger
KOPEECHKA: Final[helpers.email.Kopeechka] = helpers.email.Kopeechka(
    api_key=helpers.utils.config.kopeechka_key,
    accepted_domains=helpers.utils.config.accepted_email_domains,
)


class TwitterSession:
    def __init__(self) -> None:
        self.session = httpx.Client(
            http2=True,
            verify=helpers.utils.get_context(),
            timeout=15,
            proxies=helpers.utils.get_random_proxies(),
        )
        self.name = random.choice([FAKE.name(), random.choice(helpers.utils.usernames)])
        self.device_token = helpers.twitter.device_token()
        self.device_id, self.vendor_id, self.uuid = [
            str(uuid.uuid4()).upper() for _ in range(3)
        ]
        self.birth_day, self.birth_mont, self.birth_year = helpers.utils.birthdate()
        self.data: Dict[str, str] = {}
        self.auth = {}
        self.get_guest_token()

    @property
    def os_version(self) -> str:
        return "14.1"

    @property
    def display_size(self) -> str:
        return '1170x2532'

    @property
    def client_version(self) -> str:
        return "9.34.1"

    @property
    def user_agent(self) -> str:
        return f"Twitter-iPhone/{self.client_version} iOS/14.8 (Apple;iPhone13,2;;;;;1;2020)"

    @property
    def system_user_agent(self) -> str:
        return "Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/18A8395 Twitter for iPhone/9.29.2"

    @property
    def authorization(self) -> str:
        return "AAAAAAAAAAAAAAAAAAAAAAj4AQAAAAAAPraK64zCZ9CSzdLesbE7LB%2Bw4uE%3DVJQREvQNCZJNiz3rHO7lOXlkVOQkzzdsgu6wWgcazdMUaGoUGm"

    @property
    def basic_headerss(self) -> Dict[str, str]:
        return {
            **self.session.headers,
            "content-type": "application/json",
            "host": "api.twitter.com",
            "x-twitter-client-deviceid": self.device_id,
            "accept": "application/json",
            "x-twitter-client-version": self.client_version,
            "x-client-uuid": self.uuid,
            "x-twitter-client-language": "en",
            "x-b3-traceid": helpers.twitter.trace_id(),
            "authorization": f"Bearer {self.authorization}",
            "accept-language": "en",
            "user-agent": self.user_agent,
            "x-twitter-client-limit-ad-tracking": "0",
            "x-twitter-api-version": "5",
            "x-twitter-client": "Twitter-iPhone",
        }

    @property
    def basic_headers(self) -> Dict[str, str]:
        return {
            'host': 'api.twitter.com',
            'x-twitter-client-deviceid': self.device_id,
            'accept': 'application/json',
            'x-twitter-client-version': self.client_version,
            'x-guest-token': self.session.headers['x-guest-token'],
            'x-client-uuid': self.uuid,
            'x-twitter-client-language': 'en',
            'x-b3-traceid': helpers.twitter.trace_id(),
            'authorization': f'Bearer {self.authorization}',
            'accept-language': 'en',
            'user-agent': self.user_agent,
            'x-twitter-client-limit-ad-tracking': '0',
            'x-twitter-api-version': '5',
            'x-twitter-client': 'Twitter-iPhone',
        }

    @property
    def advanced_headers(self) -> Dict[str, str]:
        return {
            **self.session.headers,
            "twitter-display-size": self.display_size,
            "x-twitter-client-vendorid": self.vendor_id,
            "system-user-agent": self.system_user_agent,
            "x-b3-traceid": helpers.twitter.trace_id(),
            "content-type": "application/json",
            "os-version": self.os_version,
        }

    @property
    def authed_headers(self) -> Dict[str, str]:
        return {
            **self.advanced_headers,
            "timezone": "",
            "kdt": self.auth["kdt"],
            "x-twitter-active-user": "yes",
            "system-user-agent": self.system_user_agent,
            "authorization": helpers.oauth.getAuth(
                "POST",
                helpers.constants.BASE_URL,
                self.auth["oauth_secret"],
                self.auth["oauth_token"],
                None,
            ),
        }

    def get_guest_token(self) -> None:
        headers = {
           "host": "api.twitter.com",
           "content-type": "application/x-www-form-urlencoded",
           "x-twitter-client-deviceid": self.device_id,
           "accept": "application/json",
           "x-twitter-client-version": self.client_version,
           "authorization": f"Bearer {self.authorization}",
           "x-client-uuid": self.uuid,
           "x-twitter-client-language": "en",
           "x-b3-traceid": helpers.twitter.trace_id(),
           "accept-language": "en",
           "accept-encoding": "gzip, deflate, br",
           "user-agent": self.user_agent,
           "x-twitter-client-limit-ad-tracking": "0",
           "x-twitter-api-version": "5",
           "x-twitter-client": "Twitter-iPhone",
        }
        if 'connection' in self.session.headers:
            del self.session.headers['connection']
        response = self.session.post("https://api.twitter.com/1.1/guest/activate.json", headers=headers) #TODO: Headers order is very important

        gt = response.json().get("guest_token")
        if gt:
            self.session.headers["x-guest-token"] = gt
        else:
            raise exceptions.GuestTokenError("Failed grabbing guest token")

    def init_flow_token(self) -> str:
        url = 'https://api.twitter.com/1.1/onboarding/task.json?' + f'api_version=2&ext=highlightedLabel%2CmediaColor&flow_name=welcome&include_entities=1&include_profile_interstitial_type=true&include_profile_location=true&include_user_entities=true&include_user_hashtag_entities=true&include_user_mention_entities=true&include_user_symbol_entities=true&known_device_token={self.device_token}&sim_country_code=GB'
        headers = {
            'host': 'api.twitter.com',
            'user-agent': self.user_agent,
            'x-twitter-client': 'Twitter-iPhone',
            'x-twitter-client-deviceid': self.device_id,
            'twitter-display-size': '1170x2532',
            'x-twitter-client-vendorid': self.vendor_id,
            'system-user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/18A8395 Twitter for iPhone/9.29.2',
            'x-twitter-client-version': self.client_version,
            'x-twitter-client-limit-ad-tracking': '0',
            'x-b3-traceid': helpers.twitter.trace_id(),
            'x-guest-token': self.session.headers['x-guest-token'],
            'accept-language': 'en',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAAAj4AQAAAAAAPraK64zCZ9CSzdLesbE7LB%2Bw4uE%3DVJQREvQNCZJNiz3rHO7lOXlkVOQkzzdsgu6wWgcazdMUaGoUGm',
            'x-twitter-client-language': 'en',
            'x-client-uuid': self.uuid,
            'x-twitter-api-version': '5',
            'accept': 'application/json',
            'content-type': 'application/json',
            'os-version': '14.1',
            'accept-encoding': 'gzip, deflate, br'
        }
        response = self.session.post(
            url,
            headers=headers,
            json=helpers.constants.FLOW_INIT_PAYLOAD,
        )
        jsn = response.json()
        if jsn.get("status", "") == "success":
            return jsn["flow_token"]
        raise exceptions.FlowInitError(f"Error while initiating signup flow: {jsn}")

    def send_phone_otp(
        self, phone_number: str, phone_country: str, flow_token: str
    ) -> bool:
        payload = {
            "phone": phone_number,
            "sim_country_code": phone_country.upper(),
            "flow_token": flow_token,
            "use_voice": "false",
        }
        resp = self.session.post(
            "https://api.twitter.com/1.1/onboarding/begin_verification.json",
            json=payload,
            headers=self.basic_headers,
        )
        return "normalized_phone_number" in resp.text

    def send_email_otp(self, email: str, flow_token: str) -> bool:
        headers = {
            'host': 'api.twitter.com',
            'x-twitter-client-deviceid': self.device_id,
            'accept': 'application/json',
            'x-twitter-client-version': self.client_version,
            'x-guest-token': self.session.headers['x-guest-token'],
            'x-client-uuid': self.uuid,
            'x-twitter-client-language': 'en',
            'x-b3-traceid': helpers.twitter.trace_id(),
            'authorization': f'Bearer {self.authorization}',
            'accept-language': 'en',
            'user-agent': self.user_agent,
            'x-twitter-client-limit-ad-tracking': '0',
            'x-twitter-api-version': '5',
            'x-twitter-client': 'Twitter-iPhone'
        }
        payload = {
            "email": email,
            "display_name": self.name.replace(" ", ""),
            "flow_token": flow_token,
            "use_voice": "false",
        }
        response = self.session.post(
            "https://api.twitter.com/1.1/onboarding/begin_verification.json",
            json=payload,
            headers=headers,
        )
        return response.status_code == 204

    def phone_code_flow(
        self,
        phone_number: str,
        otp_code: str,
        flow_token: str,
        js_instrumentation: Dict[str, str],
        captcha_key: str,
    ) -> str:
        payload = helpers.constants.PHONE_CODE_PAYLOAD
        input_tasks = payload["subtask_inputs"]

        payload["flow_token"] = flow_token
        input_tasks[3]["completion_deeplink"] = input_tasks[3][
            "completion_deeplink"
        ].replace("captchatokenhere", captcha_key)
        input_tasks[2]["sign_up"]["js_instrumentation"]["response"] = js_instrumentation
        input_tasks[2]["sign_up"]["birthday"]["day"] = self.birth_day
        input_tasks[2]["sign_up"]["birthday"]["month"] = self.birth_mont
        input_tasks[2]["sign_up"]["birthday"]["year"] = self.birth_year
        input_tasks[2]["sign_up"]["name"] = self.name
        input_tasks[2]["sign_up"]["phone_number"] = phone_number
        input_tasks[-1]["phone_verification"]["code"] = otp_code
        input_tasks[-1]["phone_verification"]["normalized_phone"] = phone_number

        response = self.session.post(
            helpers.constants.BASE_URL,
            params=helpers.constants.GENERAL_PARAMS,
            json=payload,
            headers=self.advanced_headers,
        )

        jsn = response.json()
        if jsn.get("status", "") == "success":
            return jsn["flow_token"]
        raise exceptions.PhoneFlowError(f"Error while Completing phone flow: {jsn}")

    def email_code_flow(
        self,
        email: str,
        otp_code: str,
        flow_token: str,
        js_instrumentation: str,
        captcha_key: str,
    ) -> str:
        headers = {
            'host': 'api.twitter.com',
            'user-agent': self.user_agent,
            'x-twitter-client': 'Twitter-iPhone',
            'x-twitter-client-deviceid': self.device_id,
            'x-guest-token': self.session.headers['x-guest-token'],
            'twitter-display-size': self.display_size,
            'x-twitter-client-vendorid': self.vendor_id,
            'system-user-agent': self.system_user_agent,
            'x-twitter-client-version': self.client_version,
            'x-twitter-client-limit-ad-tracking': '0',
            'x-b3-traceid': helpers.twitter.trace_id(),
            'accept-language': 'en',
            'authorization': f'Bearer {self.authorization}',
            'x-twitter-client-language': 'en',
            'x-client-uuid': self.uuid,
            'x-twitter-api-version': '5',
            'accept': 'application/json',
            'content-type': 'application/json',
            'os-version': '14.1',
        }

        payload = {
            "flow_token": flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": "SplashScreenWithSso",
                    "cta": {
                        "link": "signup",
                        "component_values": []
                    }
                },
                {
                    "subtask_id": "WelcomeFlowStartSignupOpenLink",
                    "open_link": {
                        "link": "welcome_flow_start_signup",
                        "component_values": []
                    }
                },
                {
                    "subtask_id": "Signup",
                    "sign_up": {
                        "email": email,
                        "js_instrumentation": {
                            "response": js_instrumentation
                        },
                        "name": self.name,
                        "birthday": {
                            "year": self.birth_year,
                            "month": self.birth_mont,
                            "day": self.birth_day
                        },
                        "link": "email_next_link"
                    }
                },
                {"subtask_id":"ArkosePhone","web_modal":{"completion_deeplink":"twitter://onboarding/web_modal/next_link?access_token="+ captcha_key +"","link":"signup_with_phone_next_link"}},
                {
                    "subtask_id": "SignupSettingsListEmailNonEU",
                    "settings_list": {
                        "link": "next_link",
                        "component_values": [],
                        "setting_responses": [
                            {
                                "key": "twitter_for_web",
                                "response_data": {
                                    "boolean_data": {
                                        "result": 'false'
                                    }
                                }
                            }
                        ]
                    }
                },
                {
                    "subtask_id": "SignupReview",
                    "sign_up_review": {
                        "link": "signup_with_email_next_link",
                        "component_values": []
                    }
                },
                {
                    "subtask_id": "EmailVerification",
                    "email_verification": {
                        "code": otp_code,
                        "component_values": [],
                        "email": email,
                        "link": "next_link"
                    }
                }
            ]
        }

        response = self.session.post(
            "https://api.twitter.com/1.1/onboarding/task.json?ext=highlightedLabel%2CmediaColor&include_entities=1&include_profile_interstitial_type=true&include_profile_location=true&include_user_entities=true&include_user_hashtag_entities=true&include_user_mention_entities=true&include_user_symbol_entities=true",
            json=payload,
            headers=headers,
        )

        jsn = response.json()
        if jsn.get("status", "") == "success":
            return jsn["flow_token"]
        raise exceptions.EmailFlowError(f"Error while Completing email flow: {jsn}")

    def password_flow(self, flow_token: str, password: str) -> str:
        headers = {
            'host': 'api.twitter.com',
            'user-agent': self.user_agent,
            'x-twitter-client': 'Twitter-iPhone',
            'x-twitter-client-deviceid': self.device_id,
            'x-guest-token': self.session.headers['x-guest-token'],
            'twitter-display-size': self.display_size,
            'x-twitter-client-vendorid': self.vendor_id,
            'system-user-agent': self.system_user_agent,
            'x-twitter-client-version': self.client_version,
            'x-twitter-client-limit-ad-tracking': '0',
            'x-b3-traceid': helpers.twitter.trace_id(),
            'accept-language': 'en',
            'authorization': f'Bearer {self.authorization}',
            'x-twitter-client-language': 'en',
            'x-client-uuid': self.uuid,
            'x-twitter-api-version': '5',
            'accept': 'application/json',
            'content-type': 'application/json',
            'os-version': '14.1',
        }
        payload = {
            "flow_token": flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": "EnterPassword",
                    "enter_password": {
                        "link": "next_link",
                        "component_values": [],
                        "password": password
                    }
                }
            ]
        }

        response = self.session.post(
            "https://api.twitter.com/1.1/onboarding/task.json?ext=highlightedLabel%2CmediaColor&include_entities=1&include_profile_interstitial_type=true&include_profile_location=true&include_user_entities=true&include_user_hashtag_entities=true&include_user_mention_entities=true&include_user_symbol_entities=true",
            json=payload,
            headers=headers,
        )
        jsn = response.json()
        if jsn.get("status", "") == "success":
            LOGGER.info("Completed password flow")
            self.auth["kdt"] = response.headers.get("kdt", "")
            self.auth["oauth_token"] = jsn["subtasks"][0]["open_account"]["oauth_token"]
            self.auth["oauth_secret"] = jsn["subtasks"][0]["open_account"][
                "oauth_token_secret"
            ]
            return jsn["flow_token"]

        raise exceptions.PasswordFlowError(
            f"Error while filling out password flow: {jsn}"
        )

    def StartSetup(self, flow_token: str):
        if "EnterProfileBio" in self.data:
            self.bio_flow(flow_token)
        elif "Avatar" in self.data:
            self.avatar_flow(flow_token)
        elif "Username" in self.data:
            self.username_flow(flow_token)
        elif "Notifications" in self.data:
            self.notification_flow(flow_token)
        elif self.data == "PermissionPrompt":
            self.permission_flow(flow_token)
        elif self.data == "LanguageSelectorList":
            self.language_flow(flow_token)

    def avatar_flow(self, flow_token: str) -> None:
        payload = {
            "flow_token": flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": "OpenAccount",
                    "open_account": {
                        "link": "next_link",
                        "component_values": []
                    }
                },
                {
                    "subtask_id": "WelcomeFlowStartAccountSetupOpenLink",
                    "open_link": {
                        "link": "welcome_flow_start_account_setup",
                        "component_values": []
                    }
                },
                {
                    "subtask_id": "SelectAvatar",
                    "select_avatar": {
                        "link": "next_link",
                        "component_values": []
                    }
                },
                {
                    "subtask_id": "UploadMedia",
                    "upload_media": {
                        "link": "next_link",
                        "component_values": []
                    }
                }
            ]
        }

        headers = {
            'host': 'api.twitter.com',
            'kdt': self.auth['kdt'],
            'user-agent': self.user_agent,
            'x-twitter-client': 'Twitter-iPhone',
            'x-twitter-client-deviceid': self.device_id,
            'x-twitter-active-user': 'yes',
            'twitter-display-size': self.display_size,
            'x-twitter-client-vendorid': self.vendor_id,
            'system-user-agent': self.system_user_agent,
            'x-twitter-client-version': self.client_version,
            'x-twitter-client-limit-ad-tracking': '0',
            'x-b3-traceid': helpers.twitter.trace_id(),
            'accept-language': 'en',
            'timezone': '',
            'authorization': helpers.oauth.getAuth("POST","https://api.twitter.com/1.1/onboarding/task.json",self.auth["oauth_secret"],self.auth["oauth_token"],None),
            'x-twitter-client-language': 'en',
            'x-client-uuid': self.uuid,
            'x-twitter-api-version': '5',
            'accept': 'application/json',
            'content-type': 'application/json',
            'os-version': self.os_version,
        }

        response = self.session.post(
            "https://api.twitter.com/1.1/onboarding/task.json?ext=highlightedLabel%2CmediaColor&include_entities=1&include_profile_interstitial_type=true&include_profile_location=true&include_user_entities=true&include_user_hashtag_entities=true&include_user_mention_entities=true&include_user_symbol_entities=true",
            json=payload,
            headers=headers,
        )

        jsn = response.json()
        if jsn.get("status", "") == "success":
            self.data = jsn["subtasks"][0]["subtask_id"]
            self.StartSetup(jsn["flow_token"])
        else:
            raise exceptions.AvatarFlowError(f"Error while Setting Avatar: {jsn}")

    def bio_flow(self, flow_token: str) -> None:
        payload = {
            "flow_token": flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": self.data,
                    "enter_text": {
                        "link": "skip_link",
                        "component_values": [],
                    }
                }
            ]
        }
        headers = {
            'host': 'api.twitter.com',
            'user-agent': self.user_agent,
            'x-twitter-client': 'Twitter-iPhone',
            'x-twitter-client-deviceid': self.device_id,
            'x-twitter-active-user': 'yes',
            'twitter-display-size': self.display_size,
            'kdt': self.auth['kdt'],
            'x-twitter-client-vendorid': self.vendor_id,
            'system-user-agent': self.system_user_agent,
            'x-twitter-client-version': self.client_version,
            'x-twitter-client-limit-ad-tracking': '0',
            'x-b3-traceid': helpers.twitter.trace_id(),
            'accept-language': 'en',
            'timezone': '',
            'authorization': helpers.oauth.getAuth("POST", "https://api.twitter.com/1.1/onboarding/task.json",self.auth["oauth_secret"],self.auth["oauth_token"], None),
            'x-twitter-client-language': 'en',
            'x-client-uuid': self.uuid,
            'x-twitter-api-version': '5',
            'accept': 'application/json',
            'content-type': 'application/json',
            'os-version': self.os_version,
        }
        response = self.session.post(
            "https://api.twitter.com/1.1/onboarding/task.json?ext=highlightedLabel%2CmediaColor&include_entities=1&include_profile_interstitial_type=true&include_profile_location=true&include_user_entities=true&include_user_hashtag_entities=true&include_user_mention_entities=true&include_user_symbol_entities=true",
            json=payload,
            headers=headers,
        )
        jsn = response.json()
        if jsn.get("status", "") == "success":
            LOGGER.debug("[+] Set BIO")
            self.data = jsn["subtasks"][0]["subtask_id"]
            self.StartSetup(jsn["flow_token"])
        else:
            raise exceptions.BioFlowError(f"Error while Setting Bio: {jsn}")

    def username_flow(self, flow_token: str) -> None:
        payload = {
            "flow_token": flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": self.data,
                    "enter_username": {
                        "link": "next_link",
                        "component_values": [],
                        "username": ""
                    }
                }
            ]
        }
        input_tasks = payload["subtask_inputs"]
        headers = {
            'host': 'api.twitter.com',
            'user-agent': self.user_agent,
            'x-twitter-client': 'Twitter-iPhone',
            'x-twitter-client-deviceid': self.device_id,
            'x-twitter-active-user': 'yes',
            'twitter-display-size': self.display_size,
            'kdt': self.auth['kdt'],
            'x-twitter-client-vendorid': self.vendor_id,
            'system-user-agent': self.system_user_agent,
            'x-twitter-client-version': self.client_version,
            'x-twitter-client-limit-ad-tracking': '0',
            'x-b3-traceid': helpers.twitter.trace_id(),
            'accept-language': 'en',
            'timezone': '',
            'authorization': helpers.oauth.getAuth("POST","https://api.twitter.com/1.1/onboarding/task.json",self.auth["oauth_secret"],self.auth["oauth_token"],None),
            'x-twitter-client-language': 'en',
            'x-client-uuid': self.uuid,
            'x-twitter-api-version': '5',
            'accept': 'application/json',
            'content-type': 'application/json',
            'os-version': '14.1',
        }
        if helpers.utils.config.use_username:
            username = helpers.utils.get_random_username()
            input_tasks[0]["enter_username"]["username"] = username
        else:
            username = FAKE.user_name()[:15]
            username = helpers.utils.fill_remaining_chars(username)
            input_tasks[0]["enter_username"]["username"] = username

        response = self.session.post(
            "https://api.twitter.com/1.1/onboarding/task.json?ext=highlightedLabel%2CmediaColor&include_entities=1&include_profile_interstitial_type=true&include_profile_location=true&include_user_entities=true&include_user_hashtag_entities=true&include_user_mention_entities=true&include_user_symbol_entities=true",
            json=payload,
            headers=headers,
        )
        jsn = response.json()
        if jsn.get("status", "") == "success":
            LOGGER.debug("[+] Set Username")
            self.data = jsn["subtasks"][0]["subtask_id"]
            self.StartSetup(jsn["flow_token"])
        else:
            raise exceptions.UsernameFlowError(f"Error while Setting Username: {jsn}")

    def notification_flow(self, flow_token: str) -> None:
        payload = {
            "flow_token": flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": self.data,
                    "notifications_permission_prompt": {
                        "link": "skip_link",
                        "component_values": []
                    }
                }
            ]
        }
        headers = {
            'host': 'api.twitter.com',
            'user-agent': self.user_agent,
            'x-twitter-client': 'Twitter-iPhone',
            'x-twitter-client-deviceid': self.device_id,
            'x-twitter-active-user': 'yes',
            'twitter-display-size': self.display_size,
            'kdt': self.auth['kdt'],
            'x-twitter-client-vendorid': self.vendor_id,
            'system-user-agent': self.system_user_agent,
            'x-twitter-client-version': self.client_version,
            'x-twitter-client-limit-ad-tracking': '0',
            'x-b3-traceid': helpers.twitter.trace_id(),
            'accept-language': 'en',
            'timezone': '',
            'authorization': helpers.oauth.getAuth("POST","https://api.twitter.com/1.1/onboarding/task.json",self.auth["oauth_secret"],self.auth["oauth_token"],None),
            'x-twitter-client-language': 'en',
            'x-client-uuid': self.uuid,
            'x-twitter-api-version': '5',
            'accept': 'application/json',
            'content-type': 'application/json',
            'os-version': self.os_version,
        }

        response = self.session.post(
            "https://api.twitter.com/1.1/onboarding/task.json?ext=highlightedLabel%2CmediaColor&include_entities=1&include_profile_interstitial_type=true&include_profile_location=true&include_user_entities=true&include_user_hashtag_entities=true&include_user_mention_entities=true&include_user_symbol_entities=true",
            json=payload,
            headers=headers,
        )
        jsn = response.json()
        if jsn.get("status", "") == "success":
            LOGGER.debug("[+] Set Notifications")
            self.data = jsn["subtasks"][0]["subtask_id"]
            self.StartSetup(jsn["flow_token"])
        else:
            raise exceptions.NotificationsFlowError(
                f"Error while Setting notifications: {jsn}"
            )

    def permission_flow(self, flow_token: str) -> None:
        payload = {
            "flow_token": flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": self.data,
                    "contacts_live_sync_permission_prompt": {
                        "link": "skip_link",
                        "component_values": []
                    }
                }
            ]
        }
        headers = {
            'host': 'api.twitter.com',
            'user-agent': self.user_agent,
            'x-twitter-client': 'Twitter-iPhone',
            'x-twitter-client-deviceid': self.device_id,
            'x-twitter-active-user': 'yes',
            'kdt': self.auth['kdt'],
            'twitter-display-size': self.display_size,
            'x-twitter-client-vendorid': self.vendor_id,
            'system-user-agent': self.system_user_agent,
            'x-twitter-client-version': self.client_version,
            'x-twitter-client-limit-ad-tracking': '0',
            'x-b3-traceid': helpers.twitter.trace_id(),
            'accept-language': 'en',
            'timezone': '',
            'authorization': helpers.oauth.getAuth("POST","https://api.twitter.com/1.1/onboarding/task.json",self.auth["oauth_secret"],self.auth["oauth_token"],None),
            'x-twitter-client-language': 'en',
            'x-client-uuid': self.uuid,
            'x-twitter-api-version': '5',
            'accept': 'application/json',
            'content-type': 'application/json',
            'os-version': self.os_version,
        }

        response = self.session.post(
            "https://api.twitter.com/1.1/onboarding/task.json?ext=highlightedLabel%2CmediaColor&include_entities=1&include_profile_interstitial_type=true&include_profile_location=true&include_user_entities=true&include_user_hashtag_entities=true&include_user_mention_entities=true&include_user_symbol_entities=true",
            json=payload,
            headers=headers,
        )
        jsn = response.json()
        if jsn.get("status", "") == "success":
            LOGGER.debug("[+] Set Permissions")
            self.data = jsn["subtasks"][0]["subtask_id"]
            self.StartSetup(jsn["flow_token"])
        else:
            raise exceptions.PemissionFlowError(
                f"Error while Setting Permissions: {jsn}"
            )

    def language_flow(self, flow_token: str) -> None:
        payload = helpers.constants.LANGUAGE_FLOW_PAYLOAD
        payload["flow_token"] = flow_token
        input_tasks = payload["subtask_inputs"]
        headers = {
            'host': 'api.twitter.com',
            'user-agent': self.user_agent,
            'x-twitter-client': 'Twitter-iPhone',
            'x-twitter-client-deviceid': self.device_id,
            'x-twitter-active-user': 'yes',
            'kdt': self.auth['kdt'],
            'twitter-display-size': self.display_size,
            'x-twitter-client-vendorid': self.vendor_id,
            'system-user-agent': self.system_user_agent,
            'x-twitter-client-version': self.client_version,
            'x-twitter-client-limit-ad-tracking': '0',
            'x-b3-traceid': helpers.twitter.trace_id(),
            'accept-language': 'en',
            'timezone': '',
            'authorization': helpers.oauth.getAuth("POST","https://api.twitter.com/1.1/onboarding/task.json",self.auth["oauth_secret"],self.auth["oauth_token"],None),
            'x-twitter-client-language': 'en',
            'x-client-uuid': self.uuid,
            'x-twitter-api-version': '5',
            'accept': 'application/json',
            'content-type': 'application/json',
            'os-version': self.os_version,
        }
        input_tasks[0]["subtask_id"] = self.data

        response = self.session.post(
            helpers.constants.BASE_URL,
            json=payload,
            headers=headers,
            params=helpers.constants.GENERAL_PARAMS,
        )
        jsn = response.json()
        if jsn.get("status", "") == "success":
            LOGGER.debug("[+] Set Languages")
            self.data = jsn["subtasks"][0]["subtask_id"]
            self.StartSetup(jsn["flow_token"])
        else:
            raise exceptions.LanguageFlowError(f"Error while Setting Lanaguages: {jsn}")

    def updateProfilepic(self) -> bool:
        payload = {"image": helpers.utils.get_random_pfp()}
        headers = {
            "X-B3-TraceId": helpers.twitter.trace_id(),
            "Host": "api.twitter.com",
            "Timezone": "",
            "X-Twitter-Client-Language": "en",
            "X-Twitter-Client-Limit-Ad-Tracking": "0",
            "Accept-Language": "en",
            "User-Agent": self.user_agent,
            "kdt": self.auth['kdt'],
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Client-UUID": self.uuid,
            "X-Twitter-Client-DeviceID": self.device_id,
            "X-Twitter-Client": "Twitter-iPhone",
            "Accept": "application/json",
            "Authorization": helpers.oauth.getAuth("POST","https://api.twitter.com/1.1/onboarding/task.json",self.auth["oauth_secret"],self.auth["oauth_token"],payload),
            "X-Twitter-API-Version": "5",
            "X-Twitter-Active-User": "yes",
            "X-Twitter-Client-Version": self.client_version
        }

        response = self.session.post(
            "https://api.twitter.com/1.1/account/update_profile_image.json",
            headers=headers,
            data=payload,
        )
        if response.status_code == 200:
            LOGGER.debug("[+] Updated Profile pic")
        return response.status_code == 200

    def get_token(self) -> str:
        url = "https://api-31-0-0.twitter.com/1.1/account/settings.json?include_alt_text_compose=true&include_ext_dm_nsfw_media_filter=true&include_ext_re_upload_address_book_time=true&include_ext_sharing_audiospaces_listening_data_with_followers=true&include_ext_sso_connections=true&include_mention_filter=true&include_nsfw_admin_flag=true&include_nsfw_user_flag=true&include_universal_quality_filtering=true&protected=false"

        headers = {
            "host": "api-31-0-0.twitter.com",
            "kdt": self.auth["kdt"],
            "user-agent": self.user_agent,
            "x-twitter-client": "Twitter-iPhone",
            "x-twitter-client-deviceid": self.device_id,
            "x-twitter-active-user": "yes",
            "twitter-display-size": "1170x2532",
            "x-twitter-client-vendorid": self.vendor_id,
            "system-user-agent": self.system_user_agent,
            "x-twitter-client-version": "9.34.1",
            "x-twitter-client-limit-ad-tracking": "0",
            "x-b3-traceid": helpers.twitter.trace_id(),
            "accept-language": "en",
            "timezone": "",
            "authorization": helpers.oauth.getAuth(
                "POST",
                url,
                self.auth["oauth_secret"],
                self.auth["oauth_token"],
                "NO_VALUE",
            ),
            "x-twitter-client-language": "en",
            "x-client-uuid": self.uuid,
            "x-twitter-api-version": "5",
            "accept": "application/json",
            "content-type": "application/json",
            "os-version": "14.1",
        }
        r = self.session.post(url, headers=headers)
        url = "https://twitter.com/account/authenticate_web_view?redirect_url=https%3A%2F%2Fhelp.twitter.com%2F"

        headers = {
            "host": "twitter.com",
            "kdt": self.auth["kdt"],
            "user-agent": self.user_agent,
            "x-twitter-client": "Twitter-iPhone",
            "x-twitter-client-deviceid": self.device_id,
            "x-twitter-active-user": "yes",
            "twitter-display-size": self.display_size,
            "x-twitter-client-vendorid": self.vendor_id,
            "system-user-agent": self.system_user_agent,
            "x-twitter-client-version": self.client_version,
            "x-twitter-client-limit-ad-tracking": "0",
            "x-b3-traceid": helpers.twitter.trace_id(),
            "accept-language": "en",
            "timezone": "",
            "authorization": helpers.oauth.getAuth(
                "GET",
                url,
                self.auth["oauth_secret"],
                self.auth["oauth_token"],
                "NO_VALUE",
            ),
            "x-twitter-client-language": "en",
            "x-client-uuid": self.uuid,
            "x-twitter-api-version": "5",
            "accept": "application/json",
            "content-type": "application/json",
            "os-version": self.os_version,
        }
        r = self.session.get(url, headers=headers)
        return r.cookies["auth_token"]


class TwitterGenerator:
    def __init__(self) -> None:
        self.lock = Lock()
        self.SessionManager = helpers.twitter.SessionManager(helpers.utils.proxies)
        if not os.path.exists("output"):
            os.mkdir("output")

    def save_token(self, token: str, path: str = None) -> None:
        if path is None:
            path = "output/tokens.txt"
        with self.lock:
            with open(path, "a", encoding="utf-8") as file:
                file.write(f"{token}\n")

    def gen(self):
        while True:
            try:
                twitter = TwitterSession()
                init_token = twitter.init_flow_token()
                LOGGER.debug("[+] Initiated signup flow")
                provider = random.choice(ENABLED_SOLVERS)
                captcha_key = provider.solve_captcha()
                LOGGER.info(
                    f"[+] Solved Captcha: {captcha_key[:12]} - Solver used: {provider.name}"
                )
                with KOPEECHKA.rent_email() as (activation_id, email):
                    LOGGER.debug(f"[+] Rented email {email}")
                    sent_otp = twitter.send_email_otp(email, init_token)
                    if not sent_otp:
                        LOGGER.error("[!] Failed to send email OTP")
                    LOGGER.debug(f"[+] Sent_otp: {sent_otp}")
                    email_code = KOPEECHKA.get_code(activation_id)
                    if not email_code:
                        LOGGER.error("[!] Failed to get email code, canceling email")
                        KOPEECHKA.cancel_email(activation_id)
                        continue
                    LOGGER.info(f"[+] Got email code: {email_code}")
                    js_instrumentation = helpers.twitter.get_web_instrumentation()
                    LOGGER.debug(f"[+] JS Data: {str(js_instrumentation)[:12]}")
                    second_token = twitter.email_code_flow(
                        email, email_code, init_token, js_instrumentation, captcha_key
                    )
                    LOGGER.debug("[+] Completed email flow")
                    third_token = twitter.password_flow(
                        second_token, helpers.utils.config.account_password
                    )
                    LOGGER.debug("[+] Completed password flow")
                    twitter.avatar_flow(third_token)
                    LOGGER.debug("[+] Completed Avatar flow")
                    auth_token = twitter.get_token()
                    LOGGER.info(f"[+] Created account [{auth_token}]")
                    session = self.SessionManager.init_session(auth_token)
                    LOGGER.debug(f"[+] Initiated session Using [{auth_token}]")
                    self.save_token(
                        f"{email}:{helpers.utils.config.account_password}:{session.cookies.get('ct0', '')}:{auth_token}"
                    )
                    if helpers.utils.config.use_pfp:
                        self.SessionManager.set_pfp(session, helpers.utils.random_pfp_fiile())
            except KeyboardInterrupt:
                LOGGER.debug("[+] Exiting...")
                break
            except:
                continue


if __name__ == "__main__":
    Generator = TwitterGenerator()
    for i in range(helpers.utils.config.threads):
        Thread(target=Generator.gen).start()
