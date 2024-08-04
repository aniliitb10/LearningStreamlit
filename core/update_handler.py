from typing import Optional, Type

import pandas as pd
import streamlit as sl

from base.model import Model
from core.model_config import ModelConfig
from core.model_session_data import ModelSessionData
from core.persistence import Persistence
from core.response_data import ResponseData
from core.session_data_mgr import SessionDataMgr
from core.update_calculator import UpdateCalculator
from enums import Operation, ModelSessionDataEnum
from util import Util


class UpdateHandler:
    """ This must be created specific to a Model"""

    def __init__(self, df: pd.DataFrame, config: ModelConfig):
        self.df: pd.DataFrame = df
        self.config: ModelConfig = config
        self._data_updates: dict[Operation, pd.DataFrame] = {}
        self._model_class: Type[Model] = self.config.model_class

    def _update_data_view(self, ):
        for state in (Operation.New, Operation.Edited, Operation.Deleted):
            state_data: Optional[pd.DataFrame] = self._data_updates.get(state, None)
            if not Util.is_none_or_empty_df(state_data):
                sl.subheader(Util.colored_text(f"{state} rows", state))
                sl.dataframe(state_data, hide_index=True,
                             column_config=self._model_class.get_column_config(), use_container_width=True)

    def _update_widgets(self):
        """ As soon as there is some change, two buttons should appear - to either apply or discard the changes """
        if any([not Util.is_none_or_empty_df(df) for df in self._data_updates.values()]):
            col1, _, col2, __ = sl.columns([4, 1, 4, 20])

            with col1:
                sl.button('Discard', on_click=self._discard_changes)

            with col2:
                sl.button('Apply Changes', type="primary", on_click=self._persist_changes)

    def __call__(self, *args, **kwargs):
        model_session_data: ModelSessionData = SessionDataMgr.get_instance().get_model_data(self.config.name)
        self._data_updates = UpdateCalculator(self.df, model_session_data).calculate_update()
        self._update_data_view()
        self._update_widgets()

    def _discard_changes(self) -> None:
        """ Although, can't undo the changes in data grid, this does remove the diff created from changes """
        self._data_updates = {}
        session_data: ModelSessionData = SessionDataMgr.get_instance().get_model_data(self.config.name)
        session_data.clear_data()
        session_data.change_key(ModelSessionDataEnum.EditorData)
        sl.toast(f'All changes have been discarded', icon=":material/mood_bad:")

    def _persist_changes(self):
        """ Expected to be called by 'Apply changes' button """
        persistence = Persistence(self.config, self._data_updates)
        persistence_response: dict[Operation, Optional[ResponseData]] = persistence.persist()
        for operation, response in persistence_response.items():
            if response and not response.is_status_ok:
                Util.flash_message(sl.error, f'There was some issue in handling [{operation.value}]'
                                             f' data: {response.error_msg}')
                self._discard_changes()
                return

        # Not sure if this is really needed
        SessionDataMgr.get_instance().get_model_data(self.config.name).clear_data()
        sl.toast(f'All changes have been saved', icon=":material/sentiment_satisfied:")

