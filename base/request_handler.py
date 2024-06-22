from typing import Optional

import requests


class RequestHandler:
    """ All the Rest API calls are being made separately, so that it can be overridden by subclasses."""

    @staticmethod
    def handle_get(url: str, headers: Optional[dict[str, str]] = None) -> requests.Response:
        return requests.get(url=url, headers=headers)

    @staticmethod
    def handle_post(url: str, json_data: str, headers: dict[str, str]) -> requests.Response:
        return requests.post(url=url, data=json_data, headers=headers)

    @staticmethod
    def handle_delete(url: str, json_data: str, headers: dict[str, str]) -> requests.Response:
        return requests.delete(url=url, data=json_data, headers=headers)
