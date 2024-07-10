import pandas as pd
import streamlit as st

from config import Config
from core.persistence import Persistence
from core.response_data import ResponseData
from core.session_data_mgr import SessionDataMgr
from core.update_handler import UpdateHandler
from enums import SessionDataEnum
from util import Util


def update_table_view():
    config: Config = Config.get_instance()
    session_data_mgr = SessionDataMgr.get_instance()
    df: pd.DataFrame = session_data_mgr.get_data(SessionDataEnum.ModelTableData)

    if Util.is_none_or_empty_df(df):
        data: ResponseData = Persistence.get_model_data()
        if not data.is_valid():
            # just use empty frame to allow adding new data
            df = pd.DataFrame(columns=[column for column in config.get_model_class().get_column_config().keys()])
        else:
            df = data.df
            session_data_mgr.update_data(SessionDataEnum.ModelTableData, df)

    update_handler: UpdateHandler = UpdateHandler(df)
    st.data_editor(df, on_change=update_handler, key=session_data_mgr.get_key(SessionDataEnum.EditorData),
                   hide_index=True, num_rows="dynamic", use_container_width=True,
                   column_config=config.get_model_class().get_column_config())


def update_table_audit_view():
    config: Config = Config.get_instance()
    movie_id: int = int(st.number_input("Please enter Id", min_value=0, max_value=100_000_000, step=1))

    if movie_id <= 0:
        return

    data: ResponseData = Persistence.get_model_audit_data(model_id=movie_id)
    if not data.is_valid():
        st.error(data.error_msg, icon="🚨")
        return

    st.dataframe(data.df, use_container_width=True,
                 column_order=config.get_model_audit_class().get_column_config().keys(),
                 column_config=config.get_model_audit_class().get_column_config())


def main():
    st.set_page_config(layout='wide', initial_sidebar_state="expanded")
    main_table_data, audit_data = st.tabs(["Full Table Data", "Audit Data"])

    with main_table_data:
        update_table_view()

    with audit_data:
        update_table_audit_view()


if __name__ == '__main__':
    main()
