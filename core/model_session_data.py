from typing import Any, Optional

import pandas as pd
import streamlit

from core.editor_meta_data import EditorMetaDataConfig, EditorMetaData
from enums import SessionDataTypeEnum, Operation


class ModelSessionData:

    def __init__(self, model: str, session_data: dict[str, Any]):
        self.model = model
        self._key_map: dict[SessionDataTypeEnum, str] = EditorMetaData.get_key_map(self.model)
        self._session_data: dict[str, Any] = {}
        setattr(session_data, self.model, self._session_data)

    def update_data(self, key_enum: SessionDataTypeEnum, value: pd.DataFrame):
        self._session_data[self._key_map[key_enum]] = value

    def get_data(self, key_enum: SessionDataTypeEnum) -> Optional[pd.DataFrame]:
        return self._session_data.get(self._key_map[key_enum], None)

    def change_key(self, key_enum: SessionDataTypeEnum):
        self._session_data.pop(self._key_map[key_enum], None)
        self._key_map[key_enum] = EditorMetaData.get_new_key(self.model, key_enum)

    def get_key(self, key_enum: SessionDataTypeEnum) -> str:
        return self._key_map[key_enum]

    def get_editor_data(self, operation: Operation) -> Any:
        session_key: str = self._key_map[SessionDataTypeEnum.EditorData]
        editor_data: dict[str, Any] = streamlit.session_state.get(session_key)
        m: EditorMetaData = EditorMetaDataConfig[operation]
        return editor_data.get(m.operation_key, m.default_value)

    def clear_data(self, key_enum: SessionDataTypeEnum = None) -> None:
        if key_enum:
            self._session_data.pop(self._key_map[key_enum], None)
            return

        for key_str in self._key_map.values():
            self._session_data.pop(key_str, None)

    def __repr__(self):
        return f'model:{self.model}\n' + '\n'.join([f'{k}\n{v}' for k, v in self._session_data.items()])

    def __str__(self):
        return repr(self)
