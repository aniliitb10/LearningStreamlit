from typing import Optional

import pandas as pd
import streamlit as sl

from core.persistence import Persistence
from core.update_calculator import UpdateCalculator
from enums import Operation
from util import Util


class UpdateHandler:
    def __init__(self, df: pd.DataFrame):
        self.df: pd.DataFrame = df
        self._data_updates: dict[Operation, pd.DataFrame] = {}

    @staticmethod
    def _update_data_view(update_data: dict[Operation, pd.DataFrame]):
        for state in (Operation.New, Operation.Edited, Operation.Deleted):
            state_data: Optional[pd.DataFrame] = update_data.get(state, None)
            if not Util.is_none_or_empty_df(state_data):
                sl.subheader(Util.colored_text(f"{state} rows", state))
                sl.dataframe(state_data, hide_index=True)

    def _update_widgets(self):
        """ As soon as there is some change, two buttons should appear - to either apply or discard the changes """
        if any([not Util.is_none_or_empty_df(df) for df in self._data_updates.values()]):
            col1, _, col2, __ = sl.columns([4, 1, 4, 20])

            with col1:
                sl.button('Discard', on_click=self._discard_changes)

            with col2:
                sl.button('Apply Changes', type="primary", on_click=self._persist_changes)

    def __call__(self, *args, **kwargs):
        self._data_updates = UpdateCalculator(self.df).calculate_update()
        self._update_data_view(self._data_updates)
        self._update_widgets()

    def _discard_changes(self) -> None:
        """ Although, can't undo the changes in data grid, this does remove the diff created from changes """
        self._data_updates = {}

    def _persist_changes(self):
        """ Expected to be called by 'Apply changes' button """
        persistence = Persistence(self._data_updates)
        persistence.persist()
