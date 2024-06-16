import pandas as pd
import streamlit as st

from update_handler import UpdateHandler
from session_data import SessionData


def main():
    df: pd.DataFrame = pd.read_csv('./data/good_movies.csv')

    st.set_page_config(layout='wide', initial_sidebar_state="expanded")
    st.title("IMDB Movies")
    st.data_editor(df, on_change=UpdateHandler(df), key=SessionData.Key, hide_index=True, num_rows="dynamic",
                   width=10000)


if __name__ == '__main__':
    main()
