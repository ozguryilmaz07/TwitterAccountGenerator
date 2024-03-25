import time

import requests

from . import exceptions


class Capsolver:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.session = requests.Session()

    @property
    def name(self) -> str:
        return "Capsolver"

    @property
    def create_payload(self) -> dict:
        return {
            "clientKey": self.api_key,
            "task": {
                "type": "FunCaptchaTaskProxyLess",
                "websiteURL": "https://mobile.twitter.com/i/flow/signup",
                "websitePublicKey": "2CB16598-CB82-4CF7-B332-5990DB66F3AB",
                "funcaptchaApiJSSubdomain": "https://client-api.arkoselabs.com",
            },
        }

    def solve_captcha(self) -> str:
        task_create = self.session.post(
            "https://api.capsolver.com/createTask",
            json=self.create_payload,
        )
        task = task_create.json()
        if task.get("errorId", 1):
            raise exceptions.TaskCreateError(
                f"Error while creating task: {task['errorDescription']}"
            )
        task_id = task["taskId"]
        task_results_payload = {"clientKey": self.api_key, "taskId": task_id}

        get_task_results = self.session.post(
            "https://api.capsolver.com/getTaskResult",
            json=task_results_payload,
        )
        task_results = get_task_results.json()
        while task_results["status"] == "processing":
            task_results = self.session.post(
                "https://api.capsolver.com/getTaskResult",
                json=task_results_payload,
            ).json()
            time.sleep(2)
        if task_results["status"] == "error":
            raise exceptions.SolvingError(
                f"Error while solving task: {task_results['errorDescription']}"
            )
        return task_results["solution"]["token"]

class Yescaptcha:
    def __init__(self, api_key: str, *args, **kwargs) -> None:
        self.api_key = api_key
        self.session = requests.Session()

    @property
    def name(self) -> str:
        return "Yescaptcha"

    @property
    def create_payload(self) -> dict:
        return {
            "clientKey": self.api_key,
            "task": {
                "type": "FunCaptchaTaskProxyless",
                "websiteURL": "https://mobile.twitter.com/i/flow/signup",
                "websitePublicKey": "2CB16598-CB82-4CF7-B332-5990DB66F3AB",
                "funcaptchaApiJSSubdomain": "https://client-api.arkoselabs.com"
            }
        }

    def solve_captcha(self) -> str:
        task_create = self.session.post(
            "https://api.yescaptcha.com/createTask", json=self.create_payload
        )
        task = task_create.json()
        if task.get("errorId", 1) != 0:
            raise exceptions.TaskCreateError(
                f"Error while creating task: {task['errorDescription']} ({task['errorCode']})"
            )

        task_id = task["taskId"]
        task_results_payload = {"clientKey": self.api_key, "taskId": task_id}
        get_task_results = self.session.post(
            "https://api.yescaptcha.com/getTaskResult", json=task_results_payload
        )
        task_results = get_task_results.json()

        attempts = 0
        while task_results.get("status", "error") == "processing":
            if attempts >= 60:
                raise exceptions.SolvingError(
                    "Error while solving task: Max attempts reached"
                )
            task_results = self.session.post(
                "https://api.yescaptcha.com/getTaskResult",
                timeout=30,
                json=task_results_payload,
            ).json()
            attempts += 1
            time.sleep(2)

        if task_results["errorId"] != 0:
            raise exceptions.SolvingError(
                f"Error while solving task: {task_results['errorDescription']} ({task_results['errorCode']})"
            )
        return task_results["solution"]["gRecaptchaResponse"]
