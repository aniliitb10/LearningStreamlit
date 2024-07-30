from unittest import TestCase

import pandas as pd

from core.editor_meta_data import EditorMetaData, EditorMetaDataMap
from core.model_session_data import ModelSessionData
from core.update_calculator import UpdateCalculator
from enums import Operation, ModelSessionDataEnum


class TestUpdateCalculator(TestCase):

    def setUp(self):
        self.st_session_state = dict()
        self.model_name = "model"
        self.model_data = ModelSessionData(self.model_name, self.st_session_state)
        self.df: pd.DataFrame = pd.DataFrame(data=[[1, 2], [3, 4]], columns=["A", "B"])
        self.df_data: list[dict] = self.df.to_dict(orient="records")
        self.assertEqual(self.df_data, [{"A": 1, "B": 2}, {"A": 3, "B": 4}])

        self.calculator: UpdateCalculator = UpdateCalculator(self.df, self.model_data)

    def test__get_edited_rows(self):
        editor_meta: EditorMetaData = EditorMetaDataMap[Operation.Edited]
        key = self.model_data.get_key(ModelSessionDataEnum.EditorData)

        # the update in session state
        self.st_session_state[key] = {editor_meta.operation_key: {0: {"A": 10, "B": 20}}}
        expected_data = [{"A": 1, "B": 2, "state": "old"}, {"A": 10, "B": 20, "state": "new"}]
        self.assertEqual(expected_data, self.calculator.calculate_update()[Operation.Edited].to_dict(orient="records"))

        # let's update both rows
        self.st_session_state[key] = {editor_meta.operation_key: {0: {"A": 10, "B": 5}, 1: {"B": 20}}}
        expected_data = [{"A": 1, "B": 2, "state": "old"}, {"A": 10, "B": 5, "state": "new"},
                         {"A": 3, "B": 4, "state": "old"}, {"A": 3, "B": 20, "state": "new"}]
        self.assertEqual(expected_data, self.calculator.calculate_update()[Operation.Edited].to_dict(orient="records"))

    def test__get_new_rows(self):
        editor_meta: EditorMetaData = EditorMetaDataMap[Operation.New]
        key = self.model_data.get_key(ModelSessionDataEnum.EditorData)
        self.st_session_state[key] = {editor_meta.operation_key: self.df_data}
        self.assertEqual(self.df_data, self.calculator.calculate_update()[Operation.New].to_dict(orient="records"))

    def test__get_deleted_rows(self):
        editor_meta: EditorMetaData = EditorMetaDataMap[Operation.Deleted]
        key = self.model_data.get_key(ModelSessionDataEnum.EditorData)
        self.st_session_state[key] = {editor_meta.operation_key: [0]}
        self.assertEqual([self.df_data[0]],
                         self.calculator.calculate_update()[Operation.Deleted].to_dict(orient="records"))

        # let's delete both of them
        self.st_session_state[key] = {editor_meta.operation_key: list(range(len(self.df_data)))}
        self.assertEqual(self.df_data, self.calculator.calculate_update()[Operation.Deleted].to_dict(orient="records"))

    def test_calculate_update(self):
        key = self.model_data.get_key(ModelSessionDataEnum.EditorData)
        # add a row
        self.st_session_state[key] = {EditorMetaDataMap[Operation.New].operation_key: [{"A": 10, "B": 20}]}
        expected_new_data = [{"A": 10, "B": 20}]

        # modify a row
        self.st_session_state[key][EditorMetaDataMap[Operation.Edited].operation_key] = {0: {"A": -1, "B": -2}}
        expected_modified_data = [{"A": 1, "B": 2, "state": "old"}, {"A": -1, "B": -2, "state": "new"}]

        # deleted a row
        self.st_session_state[key][EditorMetaDataMap[Operation.Deleted].operation_key] = [1]
        expected_deleted_data = [self.df_data[1]]

        # let's see if calculator got it
        updates = self.calculator.calculate_update()
        self.assertEqual(expected_new_data, updates[Operation.New].to_dict(orient="records"))
        self.assertEqual(expected_modified_data, updates[Operation.Edited].to_dict(orient="records"))
        self.assertEqual(expected_deleted_data, updates[Operation.Deleted].to_dict(orient="records"))
