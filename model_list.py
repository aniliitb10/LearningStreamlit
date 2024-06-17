from __future__ import annotations
from typing import Optional

import pandas as pd
from pydantic import BaseModel


class ModelList(BaseModel):
    @staticmethod
    def from_df(df: pd.DataFrame) -> Optional[ModelList]:
        raise NotImplementedError()

    @staticmethod
    def get_ids(df: pd.DataFrame) -> list[int]:
        raise NotImplementedError()
