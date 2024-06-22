import pandas as pd
import streamlit as st

from config import Config
from core.persistence import Persistence
from core.session_data import SessionData
from core.update_handler import UpdateHandler


def main():
    st.set_page_config(layout='wide', initial_sidebar_state="expanded")
    st.title("IMDB Movies")

    df: pd.DataFrame = Persistence.get_data()
    update_handler: UpdateHandler = UpdateHandler(df)

    config: Config = Config.get_instance()
    st.data_editor(df, on_change=update_handler, key=SessionData.get_data_editor_key(),
                   hide_index=True, num_rows="dynamic", width=10000,
                   column_config=config.get_model_class().get_column_config())


if __name__ == '__main__':
    main()
