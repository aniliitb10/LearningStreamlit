import json
from io import StringIO
from typing import Type, Optional

import pandas as pd
import requests

from base.model import Model
from base.model_list import ModelList
from base.request_handler import RequestHandler
from config import Config
from enums import Operation, EndPoint, State
from util import Util


class Persistence:
    common_headers: dict[str, str] = {'Content-type': 'application/json', 'Accept': 'application/json'}

    def __init__(self, changed_data: dict[Operation, pd.DataFrame]):
        self._changed_data: dict[Operation, pd.DataFrame] = changed_data
        self._config: Config = Config.get_instance()
        self._model_list_class: Type[ModelList] = self._config.get_model_list_class()
        self._request_handler_class: Type[RequestHandler] = self._config.get_request_handler_class()

    def persist(self) -> dict[Operation, requests.Response]:
        return {Operation.New: self._persist_new_or_edited(Operation.New),
                Operation.Edited: self._persist_new_or_edited(Operation.Edited),
                Operation.Deleted: self._persist_deleted()}

    def _persist_new_or_edited(self, state: Operation) -> Optional[requests.Response]:
        new_data_df: pd.DataFrame = self._changed_data.get(state, None)
        if Util.is_none_or_empty_df(new_data_df):
            return None  # there wasn't any new data

        if Util.STATE_STR in new_data_df.columns:
            new_data_df = new_data_df.loc[new_data_df[Util.STATE_STR] == State.New.value]
            # intentionally not in_place, otherwise might have side effects later
            new_data_df = new_data_df.drop(Util.STATE_STR, axis=1)
            if Util.is_none_or_empty_df(new_data_df):
                return None

        model_list: ModelList = self._model_list_class.from_df(new_data_df)
        return self._request_handler_class.handle_post(url=self._config.get_end_point(EndPoint.Post),
                                                       json_data=model_list.model_dump_json(by_alias=True),
                                                       headers=self.common_headers)

    def _persist_deleted(self) -> Optional[requests.Response]:
        deleted_data: pd.DataFrame = self._changed_data.get(Operation.Deleted, None)
        if Util.is_none_or_empty_df(deleted_data):
            return None  # there wasn't any new data

        deleted_ids: list[int] = self._model_list_class.get_ids(deleted_data)
        return self._request_handler_class.handle_delete(url=self._config.get_end_point(EndPoint.Delete),
                                                         json_data=json.dumps(deleted_ids),
                                                         headers=self.common_headers)

    @staticmethod
    def get_data() -> pd.DataFrame:
        """ This might seem a little counter-intuitive - why this is static?
        - Well, it has no reason to be an instance member
        - Also, this method needs to be callable from the app (or whoever needs data)
        without creating an instance of this class
        """
        config: Config = Config.get_instance()
        df: pd.DataFrame = pd.read_json(
            StringIO(config.get_request_handler_class().handle_get(url=config.get_end_point(EndPoint.Get)).text)
        )
        model_class: Type[Model] = config.get_model_class()

        df.sort_values(by=[model_class.get_id_field()], ascending=True, inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df


if __name__ == '__main__':
    persistence = Persistence({Operation.New: pd.read_csv('../data/good_movies.csv')})
    response = persistence.persist()
    print(response)
