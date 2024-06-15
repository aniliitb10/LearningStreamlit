from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, Field


class Movie(BaseModel):
    title_id: int = Field(alias='Id')
    title: str = Field(alias='Title')
    year: int = Field(alias='Year')
    votes: int = Field(alias='Votes')
    rating: float = Field(alias='Rating')
    genres: str = Field(alias='Genres')

    def __iter__(self):
        return self.model_dump(by_alias=True).items()

    def __getitem__(self, item):
        return self.model_dump(by_alias=True)[item]

    def __len__(self):
        return len(self.model_fields.items())

    @staticmethod
    def from_df(df: pd.DataFrame) -> list[Movie]:
        return [Movie.model_validate(m) for m in df.to_dict('records')]
