from itertools import chain

import pandas as pd

from enums import State
from session_data import SessionData


class UpdateCalculator:

    def __init__(self, df: pd.DataFrame):
        self.original_df: pd.DataFrame = df

    def _get_edited_rows(self) -> pd.DataFrame:
        edited_rows: dict[int, dict] = SessionData.get_edit_data()
        edited_row_indices: list[int] = [k for k in edited_rows.keys()]
        impacted_rows: list[dict] = self.original_df.iloc[edited_row_indices].to_dict('records')

        diff: list[dict] = []
        for list_index, changed_row_id in enumerate(edited_row_indices):
            old_data_row: dict = impacted_rows[list_index]
            new_data_row: dict = dict(chain(impacted_rows[list_index].items(),
                                            edited_rows[changed_row_id].items()))
            if old_data_row != new_data_row:
                diff.append(dict(chain(old_data_row.items(), {"state": "old"}.items())))
                diff.append(dict(chain(new_data_row.items(), {"state": "new"}.items())))

        new_columns: list[str] = self.original_df.columns.to_list() + ["state"]
        return pd.DataFrame(data=diff, columns=new_columns)

    def _get_new_rows(self) -> pd.DataFrame:
        new_rows: list[dict] = SessionData.get_new_data()
        return pd.DataFrame(data=[row for row in new_rows], columns=self.original_df.columns)

    def _get_deleted_rows(self) -> pd.DataFrame:
        deleted_rows: list[int] = SessionData.get_deleted_data()
        return self.original_df.iloc[deleted_rows]

    def calculate_update(self) -> dict[State, pd.DataFrame]:
        return {State.New: self._get_new_rows(),
                State.Edited: self._get_edited_rows(),
                State.Deleted: self._get_deleted_rows()}
