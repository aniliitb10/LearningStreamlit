from __future__ import annotations

from typing import Any, Optional

import streamlit as st

from core.model_session_data import ModelSessionData


class SessionDataMgr:
    """
    Its only job it to hold the session data for all Models and behave like a singleton!
    """

    _instance: Optional[SessionDataMgr] = None

    def __init__(self, models: list[str], session_data: dict[str, Any]):

        if SessionDataMgr._instance:
            raise ValueError('SessionDataMgr is already initialized')

        self.models = models
        self.model_data: dict[str, ModelSessionData] = {m: ModelSessionData(m, session_data) for m in self.models}

        SessionDataMgr._instance = self

    def get_model_data(self, model: str) -> ModelSessionData | None:
        return self.model_data.get(model)  # better to throw key not found error instead of None

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return ('Session Data Manager\n' +
                '\n'.join([f'model:{model}, data:\n{data}\n' for model, data in self.model_data.items()]))

    @classmethod
    def reset_instance(cls):
        cls._instance = None

    @classmethod
    def has_instance(cls) -> bool:
        return cls._instance is not None

    @classmethod
    def get_instance(cls, models: list[str] = None, session_data: dict[str, Any] = None) -> SessionDataMgr:
        if models and session_data:  # if provided, the use it - helpful for testing
            cls.reset_instance()
            return SessionDataMgr(models, session_data)

        if cls._instance is None:
            # if this call is to get the instance, it has to have valid models
            cls._instance = SessionDataMgr(models, st.session_state)

        return cls._instance


if __name__ == '__main__':
    session_data_mgr: SessionDataMgr = SessionDataMgr(["movies"], {'dummy': 'data'})
    print(SessionDataMgr.get_instance())
    print(f'Test by id: {session_data_mgr is SessionDataMgr.get_instance()}')
    # SessionDataMgr({})  # must throw
