from typing import Any

from pydantic import BaseModel


class Model(BaseModel):

    @classmethod
    def get_id_field(cls):
        return 'id'

    @classmethod
    def get_column_config(cls) -> dict[str, Any]:
        return {}
