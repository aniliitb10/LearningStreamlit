from itertools import chain

import pandas as pd

from core.model_session_data import ModelSessionData
from enums import Operation, State
from util import Util


class UpdateCalculator:

    def __init__(self, df: pd.DataFrame, session_data: ModelSessionData):
        self.original_df: pd.DataFrame = df
        self.session_data: ModelSessionData = session_data

    def _get_edited_rows(self) -> pd.DataFrame:
        """ Creates two rows for changes in each row - one with original and one with new data """
        edited_rows: dict[int, dict] = self.session_data.get_editor_data(Operation.Edited)
        edited_row_indices: list[int] = [k for k in edited_rows.keys()]
        impacted_rows: list[dict] = self.original_df.iloc[edited_row_indices].to_dict('records')

        diff: list[dict] = []
        for list_index, changed_row_id in enumerate(edited_row_indices):
            old_data_row: dict = impacted_rows[list_index]
            new_data_row: dict = dict(chain(impacted_rows[list_index].items(),
                                            edited_rows[changed_row_id].items()))
            if old_data_row != new_data_row:  # don't show any changes if there is effectively no change
                diff.append(dict(chain(old_data_row.items(), {Util.STATE_STR: State.Old.value}.items())))
                diff.append(dict(chain(new_data_row.items(), {Util.STATE_STR: State.New.value}.items())))

        new_columns: list[str] = self.original_df.columns.to_list() + [Util.STATE_STR]
        return pd.DataFrame(data=diff, columns=new_columns)

    def _get_new_rows(self) -> pd.DataFrame:
        new_rows: list[dict] = self.session_data.get_editor_data(Operation.New)
        return pd.DataFrame(data=[row for row in new_rows], columns=self.original_df.columns)

    def _get_deleted_rows(self) -> pd.DataFrame:
        """ Although, st returns only the ids, but it makes sense to create the df using those ids"""
        deleted_rows: list[int] = self.session_data.get_editor_data(Operation.Deleted)
        return self.original_df.iloc[deleted_rows]

    def calculate_update(self) -> dict[Operation, pd.DataFrame]:
        """ Returns the diff for all 3 operations - addition, edit and deletion """
        return {Operation.New: self._get_new_rows(),
                Operation.Edited: self._get_edited_rows(),
                Operation.Deleted: self._get_deleted_rows()}
