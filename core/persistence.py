import json
from typing import Type, Optional

import pandas as pd
import requests

from config_parser import ConfigParser
from enums import Operation, EndPoint, State
from model.model_list import ModelList
from util import Util


class Persistence:
    common_headers: dict[str, str] = {'Content-type': 'application/json', 'Accept': 'application/json'}

    def __init__(self, changed_data: dict[Operation, pd.DataFrame]):
        self._changed_data: dict[Operation, pd.DataFrame] = changed_data
        self._config: ConfigParser = ConfigParser()
        self._model_list_class: Type[ModelList] = self._config.get_model_list_class()

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
        return requests.post(url=self._config.get_end_point(EndPoint.Post),
                             data=model_list.model_dump_json(by_alias=True),
                             headers=self.common_headers)

    def _persist_deleted(self) -> Optional[requests.Response]:
        deleted_data: pd.DataFrame = self._changed_data.get(Operation.Deleted, None)
        if Util.is_none_or_empty_df(deleted_data):
            return None  # there wasn't any new data

        deleted_ids: list[int] = self._model_list_class.get_ids(deleted_data)
        return requests.delete(url=self._config.get_end_point(EndPoint.Delete),
                               data=json.dumps(deleted_ids),
                               headers=self.common_headers)


if __name__ == '__main__':
    persistence = Persistence({Operation.New: pd.read_csv('../data/good_movies.csv')})
    response = persistence.persist()
    print(response)
