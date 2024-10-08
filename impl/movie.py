from __future__ import annotations

from datetime import date
from itertools import chain
from typing import List, Optional, Any

import pandas as pd
import streamlit as st
from pydantic import Field, ConfigDict

from base.model import Model
from base.model_list import ModelList
from enums import Operation
from util import Util


class Movie(Model):
    model_config = ConfigDict(populate_by_name=True)

    title_id: int = Field(alias='id', serialization_alias='id')
    title: str = Field(alias='title')
    year: int = Field(alias='year')
    votes: int = Field(alias='votes')
    rating: float = Field(alias='rating')
    genres: str = Field(alias='genres')

    @classmethod
    def get_column_config(cls) -> dict[str, Any]:
        return {
            "id": st.column_config.NumberColumn("Title Id", help="Id of the title", min_value=1,
                                                max_value=100_000_000_000, step=1, required=True),
            "title": st.column_config.TextColumn("Movie Title", max_chars=100, required=True),
            "year": st.column_config.NumberColumn("Release Year", min_value=1900, max_value=date.today().year + 5,
                                                  required=True),
            "votes": st.column_config.NumberColumn("Votes", min_value=1, max_value=8_000_000_000, required=True),
            "rating": st.column_config.NumberColumn("Rating", min_value=0, max_value=10, step=0.1, format="%.1f",
                                                    required=True),
            "genres": st.column_config.TextColumn("Genres", max_chars=100, validate="^[a-zA-z ,-]+$", required=True),
        }


class MoviesList(ModelList):
    model_config = ConfigDict(populate_by_name=True)
    movies: list[Movie] = Field(serialization_alias='movieEntities')

    @classmethod
    def from_df(cls, df: pd.DataFrame) -> Optional[MoviesList]:
        if Util.is_none_or_empty_df(df):
            return None

        return MoviesList(movies=[Movie.model_validate(m) for m in df.to_dict('records')])

    @classmethod
    def get_ids(cls, df: pd.DataFrame) -> list:
        if Util.is_none_or_empty_df(df):
            return []

        return [m.title_id for m in MoviesList.from_df(df).movies]


class MovieAudit(Movie):
    model_config = ConfigDict(populate_by_name=True)

    version: str = Field(alias='version')
    operation: Operation = Field(alias='operation')

    @classmethod
    def get_column_config(cls) -> dict[str, Any]:
        return dict(chain(Movie.get_column_config().items(), {
            "version": st.column_config.NumberColumn("Version #", min_value=0,
                                                     max_value=1000),
            "operation": st.column_config.TextColumn("Operation")
        }.items()))
