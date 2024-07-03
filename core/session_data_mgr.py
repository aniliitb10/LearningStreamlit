from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Union

import streamlit as st

from enums import SessionDataEnum, Operation


@dataclass
class EditorMetaData:
    operation_type: Operation
    operation_key: str
    default_value: Union[dict, list]


class SessionDataMgr:
    _instance: SessionDataMgr = None

    def __init__(self, session_data: dict[str, Any]):
        if SessionDataMgr._instance:
            return

        self.session_data: dict[str, Any] = session_data
        self.key_map: dict[SessionDataEnum, str] = {e: f'{e}_{datetime.now()}' for e in SessionDataEnum}
        self.editor_data_config: dict[Operation, EditorMetaData] = {
            Operation.New: EditorMetaData(Operation.New, "added_rows", []),
            Operation.Edited: EditorMetaData(Operation.Edited, "edited_rows", {}),
            Operation.Deleted: EditorMetaData(Operation.Deleted, "deleted_rows", []),
        }

        SessionDataMgr._instance = self

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

    @staticmethod
    def reset_instance():
        SessionDataMgr._instance = None

    @staticmethod
    def get_instance(session_data: dict[str, Any] = None):
        if session_data:  # if provided, the use it - helpful for testing
            SessionDataMgr.reset_instance()
            return SessionDataMgr(session_data)

        if SessionDataMgr._instance:
            return SessionDataMgr._instance

        return SessionDataMgr(st.session_state)


if __name__ == '__main__':
    session_data_mgr: SessionDataMgr = SessionDataMgr({'dummy': 'data'})
    print(SessionDataMgr.get_instance().session_data)
