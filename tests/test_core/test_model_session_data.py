from datetime import date
from unittest import TestCase

import pandas as pd

from core.editor_meta_data import EditorMetaData, EditorMetaDataMap
from core.model_session_data import ModelSessionData
from enums import ModelSessionDataEnum, Operation
from util import Util


class TestModelSessionData(TestCase):

    def setUp(self):
        self.st_session_state = dict()
        self.model_name = "model"
        self.model_data = ModelSessionData(self.model_name, self.st_session_state)
        self.df: pd.DataFrame = pd.DataFrame(data=[[1, 2], [3, 4]], columns=["A", "B"])

    def test_update_data(self):
        self.model_data.update_data(ModelSessionDataEnum.AuditData, self.df)
        key: str = self.model_data.get_key(ModelSessionDataEnum.AuditData)
        self.assertTrue(key.startswith(f"{self.model_name}|{ModelSessionDataEnum.AuditData}"))

        # this also shows that manually updated values are nested at 2 levels
        self.assertTrue(self.df.equals(self.st_session_state[self.model_name][key]))

        # any update should reflect that
        df: pd.DataFrame = self.df.loc[:, "A"]
        self.model_data.update_data(ModelSessionDataEnum.AuditData, df)
        self.assertFalse(self.df.equals(df))  # just to show that 2 dataframes are indeed different
        self.assertTrue(df.equals(self.st_session_state[self.model_name][key]))

    def test_get_data(self):

        model_enum: ModelSessionDataEnum = ModelSessionDataEnum.AuditData
        # update data and check the result
        self.model_data.update_data(model_enum, self.df)
        self.assertTrue(self.df.equals(self.model_data.get_data(ModelSessionDataEnum.AuditData)))
        key: str = self.model_data.get_key(ModelSessionDataEnum.AuditData)
        self.assertTrue(self.model_data.get_data(model_enum).equals(self.st_session_state[self.model_name][key]))

        # But any update should reflect that
        df: pd.DataFrame = self.df.loc[:, "A"]
        self.model_data.update_data(model_enum, df)
        self.assertTrue(self.model_data.get_data(model_enum).equals(df))

        # And there shouldn't be any other entry for other enums
        for e in ModelSessionDataEnum:
            if e == model_enum:
                continue  # It has been tested before and this enum has entries
            self.assertTrue(Util.is_none_or_empty_df(self.model_data.get_data(e)))

    @classmethod
    def validate_key(cls, key: str, model_name: str, model_enum: ModelSessionDataEnum):
        return key.startswith(f"{model_name}|{model_enum}|{date.today()}")

    def test_change_key(self):
        for e in ModelSessionDataEnum:
            old_key: str = self.model_data.get_key(e)
            self.assertTrue(self.validate_key(old_key, model_name=self.model_name, model_enum=e))

            new_key: str = self.model_data.change_key(e)
            self.assertTrue(self.validate_key(new_key, model_name=self.model_name, model_enum=e))
            self.assertNotEqual(old_key, new_key)

    def test_get_key(self):
        for e in ModelSessionDataEnum:
            key: str = self.model_data.get_key(e)
            self.assertTrue(self.validate_key(key, model_name=self.model_name, model_enum=e))

    def test_get_editor_data(self):
        """ Editor data can be updated from streamlit.session_state only"""
        operation: Operation = Operation.New
        editor_meta: EditorMetaData = EditorMetaDataMap[operation]
        editor_key: str = self.model_data.get_key(ModelSessionDataEnum.EditorData)
        sample_new_data: list[dict[str, int]] = [{"A": 10, "B": 30}]
        self.st_session_state[editor_key] = {editor_meta.operation_key: sample_new_data}
        self.assertEqual(sample_new_data, self.model_data.get_editor_data(operation))

        # other keys shouldn't have any data
        for op in Operation:
            if op == operation:
                continue  # we have already established that this operation has data
            self.assertFalse(self.model_data.get_editor_data(op))

    def test_clear_data(self):
        table_data_enum: ModelSessionDataEnum = ModelSessionDataEnum.TableData
        self.model_data.update_data(table_data_enum, self.df)

        # model data should have updates but there should be nothing in editor
        self.assertFalse(Util.is_none_or_empty_df(self.df))
        self.assertTrue(self.df.equals(self.model_data.get_data(table_data_enum)))
        for op in Operation:  # there should be nothing in editor
            self.assertFalse(self.model_data.get_editor_data(op))

        # now clearing up the model data
        self.model_data.clear_data(table_data_enum)
        self.assertFalse(Util.is_none_or_empty_df(self.df))
        self.assertTrue(Util.is_none_or_empty_df(self.model_data.get_data(table_data_enum)))

        # let's just modify session data
        operation = Operation.New
        key_str: str = self.model_data.get_key(ModelSessionDataEnum.EditorData)
        data: list[dict[str, int]] = [{"A": 10, "B": 30}]
        editor_meta: EditorMetaData = EditorMetaDataMap[operation]
        self.st_session_state[key_str] = {editor_meta.operation_key: data}
        self.assertEqual(data, self.model_data.get_editor_data(operation))

        # this should not impact editor data
        self.model_data.clear_data(ModelSessionDataEnum.TableData)
        self.assertEqual(data, self.model_data.get_editor_data(operation))

        # but now, editor data should be gone
        self.model_data.clear_data(ModelSessionDataEnum.EditorData)
        self.assertFalse(self.model_data.get_editor_data(operation))

        # this could be achieved with global clear as well (without passing any arguments)
        self.st_session_state[key_str] = {editor_meta.operation_key: data}
        self.assertEqual(data, self.model_data.get_editor_data(operation))
        self.model_data.clear_data()
        self.assertFalse(self.model_data.get_editor_data(operation))
