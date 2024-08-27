import time
from pathlib import Path

import pandas as pd

from enums import Color, Operation


class Util:
    STATE_COLOR_MAP: dict[Operation, Color] = {Operation.New: Color.Green, Operation.Edited: Color.Orange,
                                               Operation.Deleted: Color.Red}
    STATE_STR = "state"

    @staticmethod
    def colored_text(text: str, state: Operation):
        """ This is as per the scheme supported by streamlit framework"""
        return f':{Util.STATE_COLOR_MAP[state]}[{text}]'

    @staticmethod
    def is_none_or_empty_df(df: pd.DataFrame) -> bool:
        return df is None or df.shape[0] == 0 or df.dropna(how='all').shape[0] == 0

    @staticmethod
    def flash_message(handler, message: str, icon: str = "🚨", seconds: int = 5):
        alert = handler(message, icon=icon)
        time.sleep(seconds)
        alert.empty()

    @staticmethod
    def file_must_exist(file_path: Path) -> None:
        if not isinstance(file_path, Path):
            raise TypeError(f"'{file_path}' [{type(file_path)}] is not a Path object")

        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"'{file_path}' file does not exist")