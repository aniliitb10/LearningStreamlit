import pandas as pd

from enums import Color, State


class Util:
    STATE_COLOR_MAP: dict[State, Color] = {State.New: Color.Green, State.Edited: Color.Orange, State.Deleted: Color.Red}

    @staticmethod
    def colored_text(text: str, state: State):
        """ This is as per the scheme supported by streamlit framework"""
        return f':{Util.STATE_COLOR_MAP[state]}[{text}]'

    @staticmethod
    def is_empty_df(df: pd.DataFrame) -> bool:
        return df is None or df.shape[0] == 0
