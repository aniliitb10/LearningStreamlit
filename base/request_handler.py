from streamlit.logger import get_logger
from io import StringIO
from typing import Optional

import pandas as pd
import requests

from core.response_data import ResponseData
from util import Util

logger = get_logger(__name__.split('.')[-1])


class RequestHandler:
    """ All the Rest API calls are being made separately, so that it can be overridden by subclasses. """

    @classmethod
    def handle_get(cls, url: str, headers: Optional[dict[str, str]] = None) -> ResponseData:
        logger.info(f"Get request: {url}")
        return cls._wrap(requests.get(url=url, headers=headers))

    @classmethod
    def handle_post(cls, url: str, json_data: str, headers: dict[str, str]) -> ResponseData:
        logger.info(f"Post request: {url}, json_data: {json_data}")
        return cls._wrap(requests.post(url=url, data=json_data, headers=headers))

    @classmethod
    def handle_put(cls, url: str, json_data: str, headers: dict[str, str]) -> ResponseData:
        logger.info(f"Put request: {url}, json_data: {json_data}")
        return cls._wrap(requests.put(url=url, data=json_data, headers=headers))

    @classmethod
    def handle_delete(cls, url: str, json_data: str, headers: dict[str, str]) -> ResponseData:
        logger.info(f"Delete request: {url}, json_data: {json_data}")
        return cls._wrap(requests.delete(url=url, data=json_data, headers=headers))

    @classmethod
    def _wrap(cls, response: requests.Response) -> ResponseData:
        if response.status_code == requests.codes.ok:

            # it is okay to have empty response
            df: pd.DataFrame = pd.read_json(StringIO(response.text)) if response.text else pd.DataFrame()
            if not Util.is_none_or_empty_df(df):
                return ResponseData(response.status_code, df=df)

            return ResponseData(response.status_code, error_msg="No Data")

        if response.text:
            return ResponseData(response.status_code, error_msg=response.text)

        # Now, the error message is not obvious, hence let's use what we can get from the library itself
        try:
            response.raise_for_status()  # this might enrich the error message
        except requests.exceptions.HTTPError as err:
            return ResponseData(response.status_code, error_msg=str(err))
