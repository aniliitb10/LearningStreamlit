from typing import Type

import pandas as pd
import streamlit as st

from core.model_config import ModelConfig
from core.model_session_data import ModelSessionData
from core.persistence import Persistence
from core.response_data import ResponseData
from core.session_data_mgr import SessionDataMgr
from core.update_handler import UpdateHandler
from enums import ModelSessionDataEnum
from util import Util


class PageUtil:

    @classmethod
    def update_table_view(cls, config: ModelConfig):
        model_data: ModelSessionData = SessionDataMgr.get_instance().get_model_data(config.name)
        df: pd.DataFrame = model_data.get_data(ModelSessionDataEnum.TableData)

        if Util.is_none_or_empty_df(df):
            data: ResponseData = Persistence.get_model_data(config)
            if not data.is_valid():
                # just use empty frame to allow adding new data
                df = pd.DataFrame(columns=[column for column in config.model_class.get_column_config().keys()])
            else:
                df = data.df
                model_data.update_data(ModelSessionDataEnum.TableData, df)

        update_handler: UpdateHandler = UpdateHandler(df, config)
        st.data_editor(df, on_change=update_handler, key=model_data.get_key(ModelSessionDataEnum.EditorData),
                       hide_index=True, num_rows="dynamic", use_container_width=True,
                       column_config=config.model_class.get_column_config())

    @classmethod
    def update_table_audit_view(cls, config: ModelConfig, id_type: Type[int | str]):
        if id_type is int:
            model_id: int = int(st.number_input("Please enter Id", min_value=0, max_value=100_000_000, step=1,
                                                key=f"{config.name}-number_input"))

            if model_id <= 0:
                return

        elif id_type is str:
            model_id: str = st.text_input("Please enter Id", key=f"{config.name}-string_input")
            if not model_id:
                return

        else:
            raise TypeError(f"Unsupported id type {id_type}")

        data: ResponseData = Persistence.get_model_audit_data(config, model_id=model_id)
        if not data.is_valid():
            st.error(data.error_msg, icon="🚨")
            return

        st.dataframe(data.df, use_container_width=True,
                     column_order=config.model_audit_class.get_column_config().keys(),
                     column_config=config.model_audit_class.get_column_config())
