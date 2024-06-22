from typing import Any

from pydantic import BaseModel


class Model(BaseModel):

    @staticmethod
    def get_id_field():
        return 'id'

    @staticmethod
    def get_column_config() -> dict[str, Any]:
        return {}
