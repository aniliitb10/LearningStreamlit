from io import StringIO
from typing import Optional

import pandas as pd
import requests

from base.request_handler import RequestHandler
from core.response_data import ResponseData
import json


class SuperHeroJsonRequestHandler(RequestHandler):

    @classmethod
    def for_outgoing_request(cls, json_data: str) -> str:
        json_data_dict: dict = json.loads(json_data)
        for obj in json_data_dict['superHeroDtoList']:
            obj['awards'] = [award.strip() for award in obj['awards'].split(',')]

        return json.dumps(json_data_dict)

    @classmethod
    def for_incoming_response(cls, json_data: str) -> str:
        json_data_list: list = json.loads(json_data)
        for obj in json_data_list:
            obj['awards'] = ','.join(obj['awards'])

        return json.dumps(json_data_list)

    @classmethod
    def _extract_response_data(cls, response: requests.Response) -> Optional[pd.DataFrame]:
        if response.status_code != requests.codes.ok:
            return None

        if not response.text:
            return None

        return pd.read_json(StringIO(cls.for_incoming_response(response.text)))

    @classmethod
    def handle_get(cls, url: str, headers: Optional[dict[str, str]] = None) -> ResponseData:
        return super().handle_get(url, headers)

    @classmethod
    def handle_post(cls, url: str, json_data: str, headers: dict[str, str]) -> ResponseData:
        return super().handle_post(url, cls.for_outgoing_request(json_data), headers)

    @classmethod
    def handle_put(cls, url: str, json_data: str, headers: dict[str, str]) -> ResponseData:
        return super().handle_put(url, cls.for_outgoing_request(json_data), headers)
