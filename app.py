import pandas as pd
import streamlit as st

from config import Config
from core.persistence import Persistence
from core.response_data import ResponseData
from core.session_data_mgr import SessionDataMgr, ModelSessionData
from core.update_handler import UpdateHandler
from enums import SessionDataTypeEnum
from util import Util


def update_table_view(config: Config):
    model_data: ModelSessionData = SessionDataMgr.get_instance().get_model_data(config.name)
    df: pd.DataFrame = model_data.get_data(SessionDataTypeEnum.ModelTableData)

    if Util.is_none_or_empty_df(df):
        data: ResponseData = Persistence.get_model_data(config)
        if not data.is_valid():
            # just use empty frame to allow adding new data
            df = pd.DataFrame(columns=[column for column in config.model_class.get_column_config().keys()])
        else:
            df = data.df
            model_data.update_data(SessionDataTypeEnum.ModelTableData, df)

    update_handler: UpdateHandler = UpdateHandler(df, config)
    st.data_editor(df, on_change=update_handler, key=model_data.get_key(SessionDataTypeEnum.EditorData),
                   hide_index=True, num_rows="dynamic", use_container_width=True,
                   column_config=config.model_class.get_column_config())


def update_table_audit_view(config: Config):
    movie_id: int = int(st.number_input("Please enter Id", min_value=0, max_value=100_000_000, step=1))

    if movie_id <= 0:
        return

    data: ResponseData = Persistence.get_model_audit_data(config, model_id=movie_id)
    if not data.is_valid():
        st.error(data.error_msg, icon="🚨")
        return

    st.dataframe(data.df, use_container_width=True,
                 column_order=config.model_audit_class.get_column_config().keys(),
                 column_config=config.model_audit_class.get_column_config())


def main():
    st.set_page_config(layout='wide', initial_sidebar_state="expanded")
    main_table_data, audit_data = st.tabs(["Full Table Data", "Audit Data"])

    configs: dict[str, Config] = Config.get_configs()
    with main_table_data:
        update_table_view(configs["movies"])

    with audit_data:
        update_table_audit_view(configs["movies"])


if __name__ == '__main__':
    main()
