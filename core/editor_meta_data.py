from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Union

from enums import Operation, SessionDataTypeEnum


@dataclass
class EditorMetaData:
    """
    editor_data method of streamlit maintains edited DataFrame rows in a particular format
    e.g. for any newly added rows, key is "added_rows" and value is a list of dictionaries
    So, this class is intended to hold such data together
    """
    operation_type: Operation
    operation_key: str  # like, added_rows, edited_rows or deleted_rows
    default_value: Union[dict, list]

    @staticmethod
    def get_editor_metadata_config() -> dict[Operation, EditorMetaData]:
        return {
            Operation.New: EditorMetaData(Operation.New, "added_rows", []),
            Operation.Edited: EditorMetaData(Operation.Edited, "edited_rows", {}),
            Operation.Deleted: EditorMetaData(Operation.Deleted, "deleted_rows", []),
        }

    @classmethod
    def get_key_map(cls, model: str) -> dict[SessionDataTypeEnum, str]:
        return {e: cls.get_new_key(model, e) for e in SessionDataTypeEnum}

    @classmethod
    def get_new_key(cls, model: str, session_enum: SessionDataTypeEnum) -> str:
        return f'{model}|{session_enum.value}|{datetime.now()}'


# to be used like a global variable
EditorMetaDataConfig: dict[Operation, EditorMetaData] = EditorMetaData.get_editor_metadata_config()
