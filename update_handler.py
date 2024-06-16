from typing import Optional

import pandas as pd
import streamlit as sl

from enums import State
from update_calculator import UpdateCalculator
from util import Util


class UpdateHandler:
    def __init__(self, df: pd.DataFrame):
        self.df: pd.DataFrame = df

    @staticmethod
    def _update_view(update_data: dict[State, pd.DataFrame]):
        for state in (State.New, State.Edited, State.Deleted):
            state_data: Optional[pd.DataFrame] = update_data.get(state, None)
            if state_data is not None and not Util.is_empty_df(state_data):
                sl.subheader(Util.colored_text(f"{state} rows", state))
                sl.dataframe(state_data, hide_index=True)

    def __call__(self, *args, **kwargs):
        self._update_view(UpdateCalculator(self.df).calculate_update())
