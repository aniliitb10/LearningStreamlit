from io import StringIO
from typing import Optional

import pandas as pd
import requests

from core.response_data import ResponseData
from util import Util


class RequestHandler:
    """ All the Rest API calls are being made separately, so that it can be overridden by subclasses. """

    @staticmethod
    def handle_get(url: str, headers: Optional[dict[str, str]] = None) -> ResponseData:
        return RequestHandler._wrap(requests.get(url=url, headers=headers))

    @staticmethod
    def handle_post(url: str, json_data: str, headers: dict[str, str]) -> ResponseData:
        return RequestHandler._wrap(requests.post(url=url, data=json_data, headers=headers))

    @staticmethod
    def handle_put(url: str, json_data: str, headers: dict[str, str]) -> ResponseData:
        return RequestHandler._wrap(requests.put(url=url, data=json_data, headers=headers))

    @staticmethod
    def handle_delete(url: str, json_data: str, headers: dict[str, str]) -> ResponseData:
        return RequestHandler._wrap(requests.delete(url=url, data=json_data, headers=headers))

    @staticmethod
    def _wrap(response: requests.Response) -> ResponseData:
        if response.status_code == requests.codes.ok:

            # it is okay to have empty response
            df: pd.DataFrame = pd.read_json(StringIO(response.text)) if response.text else pd.DataFrame()
            if not Util.is_none_or_empty_df(df):
                return ResponseData(response.status_code, df=df)

            return ResponseData(response.status_code, error_msg="No Data")

        if response.text:
            return ResponseData(response.status_code, error_msg=response.text)

        # Now, the error message is no obvious, hence let's use what we can get from the library itself
        try:
            response.raise_for_status()  # this might enrich the error message
        except requests.exceptions.HTTPError as err:
            return ResponseData(response.status_code, error_msg=str(err))
