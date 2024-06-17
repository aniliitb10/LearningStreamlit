from __future__ import annotations

from typing import List, Optional

import pandas as pd
from pydantic import BaseModel, Field, ConfigDict

from model_list import ModelList
from util import Util


class Movie(BaseModel):
    title_id: int = Field(alias='id', serialization_alias='id')
    title: str = Field(alias='title', serialization_alias='title')
    year: int = Field(alias='year', serialization_alias='year')
    votes: int = Field(alias='votes', serialization_alias='votes')
    rating: float = Field(alias='rating', serialization_alias='rating')
    genres: str = Field(alias='genres', serialization_alias='genres')

    # def __iter__(self):
    #     return self.model_dump(by_alias=True).items()
    #
    # def __getitem__(self, item):
    #     return self.model_dump(by_alias=True)[item]
    #
    # def __len__(self):
    #     return len(self.model_fields.items())

    # @staticmethod
    # def from_df(df: pd.DataFrame) -> list[Movie]:
    #     return [Movie.model_validate(m) for m in df.to_dict('records')]


class MoviesList(ModelList):
    model_config = ConfigDict(populate_by_name=True)
    movies: List[Movie] = Field(serialization_alias='movieEntities')

    @staticmethod
    def from_df(df: pd.DataFrame) -> Optional[BaseModel]:
        if Util.is_none_or_empty_df(df):
            return None

        return MoviesList(movies=[Movie.model_validate(m) for m in df.to_dict('records')])

    @staticmethod
    def get_ids(df: pd.DataFrame) -> list[int]:
        if Util.is_none_or_empty_df(df):
            return []

        return [m.title_id for m in MoviesList.from_df(df).movies]
