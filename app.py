import json

import pandas as pd
import requests
import streamlit as st

from config_parser import ConfigParser
from enums import EndPoint
from session_data import SessionData
from update_handler import UpdateHandler
from io import StringIO


def main():
    config_parser: ConfigParser = ConfigParser()
    df: pd.DataFrame = pd.read_json(StringIO(requests.get(url=config_parser.get_end_point(EndPoint.Get)).text))

    st.set_page_config(layout='wide', initial_sidebar_state="expanded")
    st.title("IMDB Movies")
    update_handler: UpdateHandler = UpdateHandler(df)
    st.data_editor(df, on_change=update_handler, key=SessionData.Key, hide_index=True, num_rows="dynamic", width=10000)


if __name__ == '__main__':
    main()
