from enum import Enum

import pandas as pd


class Color(Enum):
    Blue = "blue"
    Green = "green"
    Orange = "orange"
    Red = "red"
    Violet = "violet"
    Grey = "grey"
    Rainbow = "rainbow"

    def __str__(self):
        return self.value


class Util:

    @staticmethod
    def colored_text(text: str, color: Color):
        """ This is as per the scheme supported by streamlit framework"""
        return f':{color}[{text}]'

    @staticmethod
    def is_empty_df(df: pd.DataFrame) -> bool:
        return df is None or df.shape[0] == 0
