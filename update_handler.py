from itertools import chain

import pandas as pd
import streamlit as sl

from session_data import SessionData
from util import Util, Color


class UpdateHandler:

    def __init__(self, df: pd.DataFrame):
        self.original_df: pd.DataFrame = df

    def _get_edited_rows(self) -> pd.DataFrame:
        edited_rows: dict[int, dict] = SessionData.get_edit_data()
        edited_row_indices: list[int] = [k for k in edited_rows.keys()]
        impacted_rows: list[dict] = self.original_df.iloc[edited_row_indices].to_dict('records')

        diff: list[dict] = []
        for list_index, changed_row_id in enumerate(edited_row_indices):
            old_data_row: dict = dict(chain(impacted_rows[list_index].items(), {"state": "old"}.items()))
            new_data_row: dict = dict(chain(impacted_rows[list_index].items(),
                                            edited_rows[changed_row_id].items(), {"state": "new"}.items()))
            diff.append(old_data_row)
            diff.append(new_data_row)

        new_columns: list[str] = self.original_df.columns.to_list() + ["state"]
        return pd.DataFrame(data=diff, columns=new_columns)

    def _get_new_rows(self) -> pd.DataFrame:
        new_rows: list[dict] = SessionData.get_new_data()
        return pd.DataFrame(data=[row for row in new_rows], columns=self.original_df.columns)

    def _get_deleted_rows(self) -> pd.DataFrame:
        deleted_rows: list[int] = SessionData.get_deleted_data()
        return self.original_df.iloc[deleted_rows]

    def _update_new_rows(self):
        new_df: pd.DataFrame = self._get_new_rows()
        if not Util.is_empty_df(new_df):
            sl.subheader(Util.colored_text("New rows", Color.Green))
            sl.dataframe(new_df, hide_index=True)

    def _update_edited_rows(self):
        edited_rows: pd.DataFrame = self._get_edited_rows()
        if not Util.is_empty_df(edited_rows):
            sl.subheader(Util.colored_text("Updated rows", Color.Blue))
            sl.dataframe(edited_rows, hide_index=True)

    def _update_deleted_rows(self):
        deleted_df: pd.DataFrame = self._get_deleted_rows()
        if not Util.is_empty_df(deleted_df):
            sl.subheader(Util.colored_text("Deleted rows", Color.Red))
            sl.dataframe(deleted_df, hide_index=True)

    def __call__(self, *args, **kwargs):
        self._update_new_rows()
        self._update_edited_rows()
        self._update_deleted_rows()
