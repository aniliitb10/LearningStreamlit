import json
from typing import Type, Optional

import pandas as pd

from base.model import Model
from base.model_list import ModelList
from base.request_handler import RequestHandler
from config import Config
from core.response_data import ResponseData
from enums import Operation, EndPoint, State
from util import Util


class Persistence:
    common_headers: dict[str, str] = {'Content-type': 'application/json', 'Accept': 'application/json'}

    def __init__(self, config: Config, changed_data: dict[Operation, pd.DataFrame]):
        self._changed_data: dict[Operation, pd.DataFrame] = changed_data
        self._config: Config = config
        self._model_list_class: Type[ModelList] = self._config.model_list_class
        self._request_handler_class: Type[RequestHandler] = self._config.request_handler_class

    def persist(self) -> dict[Operation, Optional[ResponseData]]:
        return {Operation.New: self._persist_new(),
                Operation.Edited: self._persist_edited(),
                Operation.Deleted: self._persist_deleted()}

    def _persist_new(self) -> Optional[ResponseData]:
        new_data_df: pd.DataFrame = self._changed_data.get(Operation.New, None)
        if Util.is_none_or_empty_df(new_data_df):
            return None  # there wasn't any new data

        model_list: ModelList = self._model_list_class.from_df(new_data_df)
        return self._request_handler_class.handle_post(url=self._config.get_model_end_point(EndPoint.Post),
                                                       json_data=model_list.model_dump_json(by_alias=True),
                                                       headers=self.common_headers)

    def _persist_edited(self) -> Optional[ResponseData]:
        new_data_df: pd.DataFrame = self._changed_data.get(Operation.Edited, None)
        if Util.is_none_or_empty_df(new_data_df):
            return None  # there wasn't any new data

        # remove the existing entries of df, only retain new entries for sending it over to db
        new_data_df = new_data_df.loc[new_data_df[Util.STATE_STR] == State.New.value]

        # intentionally not in_place, otherwise might have side effects later
        new_data_df = new_data_df.drop(Util.STATE_STR, axis=1, inplace=False)
        if Util.is_none_or_empty_df(new_data_df):
            return None

        model_list: ModelList = self._model_list_class.from_df(new_data_df)
        return self._request_handler_class.handle_put(url=self._config.get_model_end_point(EndPoint.Put),
                                                      json_data=model_list.model_dump_json(by_alias=True),
                                                      headers=self.common_headers)

    def _persist_deleted(self) -> Optional[ResponseData]:
        deleted_data: pd.DataFrame = self._changed_data.get(Operation.Deleted, None)
        if Util.is_none_or_empty_df(deleted_data):
            return None  # there wasn't any new data

        deleted_ids: list[int] = self._model_list_class.get_ids(deleted_data)
        return self._request_handler_class.handle_delete(url=self._config.get_model_end_point(EndPoint.Delete),
                                                         json_data=json.dumps(deleted_ids),
                                                         headers=self.common_headers)

    @staticmethod
    def _get_data_impl(url: str, model_class: Type[Model], request_handler: Type[RequestHandler]) -> ResponseData:
        """
        This might seem a little counter-intuitive - why this is static?
        - Well, it has no reason to be an instance member
        - Also, this method needs to be callable from the app (or whoever needs data)
        without creating an instance of this class
        """
        response_data: ResponseData = request_handler.handle_get(url=url)
        if response_data.is_valid() and not Util.is_none_or_empty_df(response_data.df):
            response_data.df.sort_values(by=[model_class.get_id_field()], ascending=True, inplace=True)
            response_data.df.reset_index(drop=True, inplace=True)

        return response_data

    @staticmethod
    def get_model_data(config: Config) -> ResponseData:
        return Persistence._get_data_impl(url=config.get_model_end_point(EndPoint.Get),
                                          model_class=config.model_class,
                                          request_handler=config.request_handler_class)

    @staticmethod
    def get_model_audit_data(config: Config, model_id: int) -> ResponseData:
        return Persistence._get_data_impl(url=f'{config.get_model_audit_end_point(EndPoint.Get)}{model_id}/',
                                          model_class=config.model_audit_class,
                                          request_handler=config.request_handler_class)

# if __name__ == '__main__':
#     persistence = Persistence({Operation.New: pd.read_csv('../data/good_movies.csv')})
#     persist_response = persistence.persist()
#     print(persist_response)
