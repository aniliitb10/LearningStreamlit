from itertools import chain

import pandas as pd
import streamlit as st

df: pd.DataFrame = pd.read_csv('./data/good_movies.csv')
updated_rows: list[dict] = []


def data_editor_changed():
    global df
    global updated_rows
    changed_data: dict[int, dict] = st.session_state.ed["edited_rows"]
    changed_row_indices: list[int] = list(k for k in changed_data.keys())

    original_data: list[dict] = df.iloc[changed_row_indices].to_dict('records')
    diff = []
    updated_rows.clear()
    for list_index, changed_row_id in enumerate(changed_row_indices):
        old_data_row: dict = dict(chain(original_data[list_index].items(), {"state": "old"}.items()))
        new_data_row: dict = dict(chain(original_data[list_index].items(),
                                        changed_data[changed_row_id].items(), {"state": "new"}.items()))
        diff.append(old_data_row)
        diff.append(new_data_row)
        updated_rows.append(dict(chain(original_data[list_index].items(),
                                       changed_data[changed_row_id].items())))

    diff_columns: list[str] = df.columns.to_list() + ["state"]
    st.subheader("Edited data")
    st.dataframe(pd.DataFrame.from_records(data=diff, columns=diff_columns), hide_index=True)


st.title("IMDB Movies")
edited_df: pd.DataFrame = st.data_editor(df, on_change=data_editor_changed, key='ed', hide_index=True,
                                         num_rows="dynamic", height=35 * min(20, df.shape[0]) + 38)
