import pandas as pd
import streamlit as st

from config import Config
from core.persistence import Persistence
from core.session_data_mgr import SessionDataMgr
from core.update_handler import UpdateHandler
from enums import EndPoint, SessionDataEnum
from util import Util


def main():
    st.set_page_config(layout='wide', initial_sidebar_state="expanded")
    main_table_data, version_data = st.tabs(["Full Table Data", "Version Data"])
    session_data_mgr = SessionDataMgr.get_instance()

    with main_table_data:
        df: pd.DataFrame = session_data_mgr.get_data(SessionDataEnum.ModelTableData)
        if Util.is_none_or_empty_df(df):
            df: pd.DataFrame = Persistence.get_data()
            session_data_mgr.update_data(SessionDataEnum.ModelTableData, df)

        update_handler: UpdateHandler = UpdateHandler(df)

        config: Config = Config.get_instance()
        st.data_editor(df, on_change=update_handler, key=session_data_mgr.get_key(SessionDataEnum.EditorData),
                       hide_index=True, num_rows="dynamic", width=10000,
                       column_config=config.get_model_class().get_column_config())

    with version_data:
        movie_id: int = int(st.number_input("Please enter Id", min_value=0, max_value=100_000_000, step=1))

        if movie_id == 0:
            return

        try:
            version_df: pd.DataFrame = Persistence.get_data(
                f"{config.get_model_version_end_point(EndPoint.Get)}{movie_id}/",
                config.get_model_version_class())
        except ConnectionError as e:
            st.error(e)
            return

        if not Util.is_none_or_empty_df(version_df):
            st.dataframe(version_df, use_container_width=True)

        else:
            st.subheader(f'There are no Audit logs for [{movie_id}]')


if __name__ == '__main__':
    main()
