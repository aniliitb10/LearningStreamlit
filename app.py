from io import StringIO
from typing import Type

import pandas as pd
import requests
import streamlit as st

from config_parser import ConfigParser
from core.session_data import SessionData
from core.update_handler import UpdateHandler
from enums import EndPoint
from model.model import Model


def main():
    config_parser: ConfigParser = ConfigParser()
    df: pd.DataFrame = pd.read_json(StringIO(requests.get(url=config_parser.get_end_point(EndPoint.Get)).text))
    model_class: Type[Model] = config_parser.get_model_class()
    if model_class.get_id_field() not in df.columns:
        raise KeyError(f'[{model_class.get_id_field()}] is not in [{df.columns.tolist()}]')

    df.sort_values(by=[model_class.get_id_field()], ascending=True, inplace=True)
    df.reset_index(drop=True, inplace=True)

    st.set_page_config(layout='wide', initial_sidebar_state="expanded")
    st.title("IMDB Movies")
    update_handler: UpdateHandler = UpdateHandler(df)

    st.data_editor(df, on_change=update_handler, key=SessionData.Key,
                   hide_index=True, num_rows="dynamic", width=10000,
                   column_config=model_class.get_column_config())


if __name__ == '__main__':
    main()
