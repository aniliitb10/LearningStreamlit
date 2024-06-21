from io import StringIO
from typing import Type

import pandas as pd
import requests
import streamlit as st

from config_parser import ConfigParser
from enums import EndPoint
from model.model import Model


class SessionData:
    Key: str = "ed"
    ResetKey: str = "reset"

    @staticmethod
    def _get_session_data() -> dict[str, dict]:
        return getattr(st.session_state, SessionData.get_data_editor_key(), {})

    @staticmethod
    def get_data_editor_key() -> str:
        """ if there was a reset - key must change to refresh the data on the page"""
        if SessionData.ResetKey not in st.session_state:
            setattr(st.session_state, SessionData.ResetKey, 0)

        return f'data_editor_key_version_{st.session_state[SessionData.ResetKey]}'

    @staticmethod
    def reset_data_editor() -> None:
        if SessionData.ResetKey not in st.session_state:
            raise KeyError(f'Data editor key "{SessionData.ResetKey}" does not exist in session state')

        # this will change the key for Data Editor - hence, will change Data Editor
        st.session_state[SessionData.ResetKey] += 1

    @staticmethod
    def get_edit_data() -> dict[int, dict]:
        return SessionData._get_session_data().get("edited_rows", {})

    @staticmethod
    def get_new_data() -> list[dict]:
        return SessionData._get_session_data().get("added_rows", [])

    @staticmethod
    def get_deleted_data() -> list[int]:
        return SessionData._get_session_data().get("deleted_rows", [])

    @staticmethod
    def get_data() -> pd.DataFrame:
        config_parser: ConfigParser = ConfigParser()
        df: pd.DataFrame = pd.read_json(StringIO(requests.get(url=config_parser.get_end_point(EndPoint.Get)).text))
        model_class: Type[Model] = config_parser.get_model_class()

        df.sort_values(by=[model_class.get_id_field()], ascending=True, inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df
