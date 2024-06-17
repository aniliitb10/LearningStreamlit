import json
from typing import Type, Optional

import pandas as pd
import requests
from pydantic import BaseModel

from config_parser import ConfigParser
from enums import State, EndPoint
from model_list import ModelList
from util import Util


class Persistence:
    common_headers: dict[str, str] = {'Content-type': 'application/json', 'Accept': 'application/json'}

    def __init__(self, changed_data: dict[State, pd.DataFrame]):
        self._changed_data: dict[State, pd.DataFrame] = changed_data
        self._config: ConfigParser = ConfigParser()
        self._model_class: Type[BaseModel] = self._config.get_model_class()
        self._model_list_class: Type[ModelList] = self._config.get_model_list_class()

    # @staticmethod
    # def from_df_to_models(df: pd.DataFrame, to_model: Type[BaseModel]) -> list[BaseModel]:
    #     if Util.is_none_or_empty_df(df):
    #         return []
    #
    #     return [to_model.model_validate(m) for m in df.to_dict('records')]

    def persist(self) -> dict[State, requests.Response]:
        return {State.New: self._persist_new_edited(State.New),
                State.Edited: self._persist_new_edited(State.Edited),
                State.Deleted: self._persist_deleted()}

    def _persist_new_edited(self, state: State) -> Optional[requests.Response]:
        new_data_df: pd.DataFrame = self._changed_data.get(state, None)
        if Util.is_none_or_empty_df(new_data_df):
            print('No content')
            return None  # there wasn't any new data

        model_list: ModelList = self._model_list_class.from_df(new_data_df)
        return requests.post(url=self._config.get_end_point(EndPoint.Post),
                             data=model_list.model_dump_json(by_alias=True),
                             headers=self.common_headers)

    def _persist_deleted(self) -> Optional[requests.Response]:
        deleted_data: pd.DataFrame = self._changed_data.get(State.Deleted, None)
        if Util.is_none_or_empty_df(deleted_data):
            print('No content')
            return None  # there wasn't any new data

        deleted_ids: list[int] = self._model_list_class.get_ids(deleted_data)
        return requests.delete(url=self._config.get_end_point(EndPoint.Delete),
                               data=json.dumps(deleted_ids),
                               headers=self.common_headers)


if __name__ == '__main__':
    persistence = Persistence({State.Deleted: pd.read_csv('data/good_movies.csv')})
    response = persistence.persist()
    print(response)
