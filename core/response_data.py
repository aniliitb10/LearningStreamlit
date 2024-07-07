from typing import Optional

import pandas as pd
import requests

from util import Util


class ResponseData:
    def __init__(self, status_code: int, *, df: Optional[pd.DataFrame] = None, error_msg: Optional[str] = None):
        if Util.is_none_or_empty_df(df) and not error_msg:
            raise ValueError("Either df or error_msg must be provided")

        if not Util.is_none_or_empty_df(df) and error_msg:
            raise ValueError("Both df and error_msg are valid, seems logical error!")

        self._status_code: int = status_code
        self._df: Optional[pd.DataFrame] = df
        self._error_msg: Optional[str] = error_msg.strip() if error_msg else None

    @property
    def df(self) -> Optional[pd.DataFrame]:
        if not self._error_msg:
            return self._df

        raise ValueError(self._error_msg)

    def is_valid(self) -> bool:
        return self.is_status_ok and not Util.is_none_or_empty_df(self._df)

    @property
    def error_msg(self):
        """
        By default, error message is logged with url (e.g. look at requests.models.Response.raise_for_status)
        but it might be better to not expose such details to the user
        """
        url_details_index: int = self._error_msg.find("for url: ")
        if url_details_index != -1:
            return self._error_msg[:url_details_index].strip()

        return self._error_msg

    @property
    def error_msg_full(self):
        return self._error_msg

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def is_status_ok(self) -> bool:
        return self._status_code == requests.codes.ok

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'(status_code={self._status_code}), df={self._df}, error_msg={self._error_msg})')
