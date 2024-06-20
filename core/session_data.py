import streamlit as st


class SessionData:
    Key: str = "ed"

    @staticmethod
    def get_session_data() -> dict[str, dict]:
        return getattr(st.session_state, SessionData.Key, {})

    @staticmethod
    def get_edit_data() -> dict[int, dict]:
        return SessionData.get_session_data().get("edited_rows", {})

    @staticmethod
    def get_new_data() -> list[dict]:
        return SessionData.get_session_data().get("added_rows", [])

    @staticmethod
    def get_deleted_data() -> list[int]:
        return SessionData.get_session_data().get("deleted_rows", [])

    @staticmethod
    def reset_session_data() -> None:
        setattr(st.session_state, SessionData.Key, {})
