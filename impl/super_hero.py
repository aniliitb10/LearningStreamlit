from __future__ import annotations

from itertools import chain
from typing import Any, Optional

import pandas as pd
import streamlit as st
from pydantic import ConfigDict, Field

from base.model import Model
from base.model_list import ModelList
from enums import Operation
from util import Util


class SuperHero(Model):
    super_hero_id: str = Field(alias='superHeroId', serialization_alias='superHeroId')
    name: str = Field(alias='name', serialization_alias="name")
    imdb_link: str = Field(alias='imdbLink', serialization_alias="imdbLink")
    awards: str = Field(alias='awards', serialization_alias="awards")

    @classmethod
    def get_id_field(cls):
        return 'superHeroId'

    @classmethod
    def get_column_config(cls) -> dict[str, Any]:
        return {
            "superHeroId": st.column_config.TextColumn("Hero Id", help="Id of the Hero", max_chars=20, required=True),
            "name": st.column_config.TextColumn("Name of the Hero", max_chars=100, required=True),
            "imdbLink": st.column_config.LinkColumn("IMDB Link", display_text="https://www.imdb.com/name/(.*?)/",
                                                    required=True),
            "awards": st.column_config.TextColumn("Key Awards", max_chars=100, required=True),
        }


class SuperHeroList(ModelList):
    model_config = ConfigDict(populate_by_name=True)
    super_heros: list[SuperHero] = Field(serialization_alias='superHeroDtoList')

    @classmethod
    def from_df(cls, df: pd.DataFrame) -> Optional[SuperHeroList]:
        if Util.is_none_or_empty_df(df):
            return None

        return SuperHeroList(super_heros=[SuperHero.model_validate(m) for m in df.to_dict('records')])

    @classmethod
    def get_ids(cls, df: pd.DataFrame) -> list[str]:
        if Util.is_none_or_empty_df(df):
            return []

        return [m.super_hero_id for m in SuperHeroList.from_df(df).super_heros]


class SuperHeroAudit(SuperHero):
    model_config = ConfigDict(populate_by_name=True)

    version: str = Field(alias='version')
    operation: Operation = Field(alias='operation')

    @classmethod
    def get_column_config(cls) -> dict[str, Any]:
        return dict(chain(SuperHero.get_column_config().items(), {
            "version": st.column_config.NumberColumn("Version #", min_value=0,
                                                     max_value=1000),
            "operation": st.column_config.TextColumn("Operation")
        }.items()))
