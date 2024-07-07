from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Union, Optional

import streamlit as st

from core.singleton import Singleton
from enums import SessionDataEnum, Operation


@dataclass
class EditorMetaData:
    """
    editor_data method of streamlit maintains edited DataFrame rows in a particular format
    e.g. for any newly added rows, key is "added_rows" and value is a list of dictionaries
    So, this class is intended to hold such data together
    """
    operation_type: Operation
    operation_key: str
    default_value: Union[dict, list]

    @staticmethod
    def get_editor_data_config() -> dict[Operation, EditorMetaData]:
        return {
            Operation.New: EditorMetaData(Operation.New, "added_rows", []),
            Operation.Edited: EditorMetaData(Operation.Edited, "edited_rows", {}),
            Operation.Deleted: EditorMetaData(Operation.Deleted, "deleted_rows", []),
        }


class SessionDataMgr(Singleton):
    _instance: Optional[SessionDataMgr] = None

    def __init__(self, session_data: dict[str, Any]):
        super().__init__()
        self.session_data: dict[str, Any] = session_data
        self.key_map: dict[SessionDataEnum, str] = {e: f'{e}_{datetime.now()}' for e in SessionDataEnum}
        self.editor_data_config: dict[Operation, EditorMetaData] = EditorMetaData.get_editor_data_config()

    def clear_data(self, key_enum: SessionDataEnum = None) -> None:
        if key_enum:
            self.session_data.pop(self.key_map[key_enum], None)
            return

        for key_str in self.key_map.values():
            self.session_data.pop(key_str, None)

    def update_data(self, key_enum: SessionDataEnum, value: Any):
        self.session_data[self.key_map[key_enum]] = value

    def get_data(self, key_enum: SessionDataEnum) -> Any:
        return self.session_data.get(self.key_map[key_enum], None)

    def change_key(self, key_enum: SessionDataEnum):
        self.session_data.pop(self.key_map[key_enum], None)
        self.key_map[key_enum] = f'{key_enum}_{datetime.now()}'

    def get_key(self, key_enum: SessionDataEnum) -> str:
        return self.key_map[key_enum]

    def get_editor_data(self, operation: Operation) -> Any:
        m: EditorMetaData = self.editor_data_config[operation]
        return self.session_data.get(self.key_map[SessionDataEnum.EditorData]).get(m.operation_key, m.default_value)

    @classmethod
    def get_instance(cls, session_data: dict[str, Any] = None) -> SessionDataMgr | Singleton:
        if session_data:  # if provided, the use it - helpful for testing
            cls.reset_instance()
            return SessionDataMgr(session_data)

        if cls._instance is None:
            cls._instance = SessionDataMgr(st.session_state)

        return cls._instance


if __name__ == '__main__':
    session_data_mgr: SessionDataMgr = SessionDataMgr({'dummy': 'data'})
    print(SessionDataMgr.get_instance().session_data)
    print(f'Test by id: {session_data_mgr is SessionDataMgr.get_instance()}')
    # SessionDataMgr({})  # must throw
