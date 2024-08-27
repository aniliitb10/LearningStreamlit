from typing import Any, Optional

import pandas as pd

from core.editor_meta_data import EditorMetaDataMap, EditorMetaData
from enums import ModelSessionDataEnum, Operation


class ModelSessionData:
    """
    It is expected to store model specific data
    - Editor data will still be as per the specification provided by streamlit, i.e.
        -- streamlit.session_state will be a dictionary containing the key

    - But, we can utilize the streamlit.session_state to store model specific data.
    e.g. streamlit.session_state["model"]["model_specific_key"]
        -- And this is what the plan is!

    It is also important to maintain key as well
    - e.g. there could be multiple editor data, if key is not different, streamlit will raise warning and won't work
    - if corresponding key is changed, then streamlit reloads the data! It helps if changes are discarded from front end
    """

    def __init__(self, model: str, session_data: dict[str, Any]):
        self.model = model
        self._key_map: dict[ModelSessionDataEnum, str] = EditorMetaData.get_key_map(self.model)
        self._session_data: dict[str, Any] = {}

        # it is better to store this locally instead of referring to streamlit.session_data every time
        # - as it helps with testing
        # - but yes, if not for tests, session_data must be streamlit.session_data
        self._st_session_state: dict[str, Any] = session_data

        self._st_session_state[self.model] = self._session_data

    def update_data(self, key_enum: ModelSessionDataEnum, value: pd.DataFrame):
        self._session_data[self._key_map[key_enum]] = value

    def get_data(self, key_enum: ModelSessionDataEnum) -> Optional[pd.DataFrame]:
        return self._session_data.get(self._key_map[key_enum], None)

    def change_key(self, key_enum: ModelSessionDataEnum) -> str:
        """ To change the key of the session data type."""
        self._session_data.pop(self._key_map[key_enum], None)
        key: str = EditorMetaData.get_new_key(self.model, key_enum)
        self._key_map[key_enum] = key
        return key

    def get_key(self, key_enum: ModelSessionDataEnum) -> str:
        return self._key_map[key_enum]

    def get_editor_data(self, operation: Operation) -> Any:
        m: EditorMetaData = EditorMetaDataMap[operation]
        session_key: str = self._key_map[ModelSessionDataEnum.EditorData]
        editor_data: dict[str, Any] = self._st_session_state.get(session_key)
        if editor_data is None:
            return m.default_value  # this is helpful for testing

        return editor_data.get(m.operation_key, m.default_value)

    def clear_data(self, key_enum: ModelSessionDataEnum = None) -> None:
        if key_enum:
            if key_enum == ModelSessionDataEnum.TableData:
                self._session_data.pop(self._key_map[key_enum], None)
                return

            if key_enum == ModelSessionDataEnum.EditorData:
                self._st_session_state.pop(self._key_map[key_enum], None)
                return

        self._session_data.clear()
        self._st_session_state.clear()

    def __repr__(self):
        return f'model:{self.model}\n' + '\n'.join([f'{k}\n{v}' for k, v in self._session_data.items()])

    def __str__(self):
        return repr(self)
