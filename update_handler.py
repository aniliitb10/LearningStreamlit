from typing import Optional

import pandas as pd
import streamlit as sl

from enums import State
from update_calculator import UpdateCalculator
from util import Util
from persistence import Persistence


class UpdateHandler:
    def __init__(self, df: pd.DataFrame):
        self.df: pd.DataFrame = df
        self._data_updates: dict[State, pd.DataFrame] = {}

    @staticmethod
    def _update_data_view(update_data: dict[State, pd.DataFrame]):
        for state in (State.New, State.Edited, State.Deleted):
            state_data: Optional[pd.DataFrame] = update_data.get(state, None)
            if not Util.is_none_or_empty_df(state_data):
                sl.subheader(Util.colored_text(f"{state} rows", state))
                sl.dataframe(state_data, hide_index=True)

    def _update_widgets(self):
        if any([not Util.is_none_or_empty_df(df) for df in self._data_updates.values()]):
            col1, _, col2, __ = sl.columns([4, 1, 4, 20])

            with col1:
                apply: bool = sl.button('Apply changes', key='apply_button', on_click=self._persist_changes)

            with col2:
                discard: bool = sl.button('Discard', key='discard_button')

            if apply:
                sl.warning('Going to apply the changes')

            if discard:
                sl.warning('Going to discard the changes')

    def __call__(self, *args, **kwargs):
        self._data_updates = UpdateCalculator(self.df).calculate_update()
        self._update_data_view(self._data_updates)
        self._update_widgets()

    def has_updates(self) -> bool:
        return bool(self._data_updates)

    def _persist_changes(self):
        persistence = Persistence(self._data_updates)
        persistence.persist()
