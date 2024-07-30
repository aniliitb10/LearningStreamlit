from __future__ import annotations
from typing import Optional

import pandas as pd
from pydantic import BaseModel


class ModelList(BaseModel):
    @classmethod
    def from_df(cls, df: pd.DataFrame) -> Optional[ModelList]:
        raise NotImplementedError("from_df is not implemented")

    @classmethod
    def get_ids(cls, df: pd.DataFrame) -> list[int]:
        raise NotImplementedError("get_ids is not implemented")
