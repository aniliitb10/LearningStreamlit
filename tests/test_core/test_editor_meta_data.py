from unittest import TestCase

from core.editor_meta_data import EditorMetaData
from enums import Operation, ModelSessionDataEnum


class TestEditorMetaData(TestCase):
    def test_new_editor_metadata_config(self):
        meta_data_map: dict[Operation, EditorMetaData] = EditorMetaData.get_editor_metadata_map()
        new_meta_data: EditorMetaData = meta_data_map.get(Operation.New)
        self.assertEqual(Operation.New, new_meta_data.operation_type)
        self.assertEqual("added_rows", new_meta_data.operation_key)
        self.assertEqual([], new_meta_data.default_value)

    def test_edited_editor_metadata_config(self):
        meta_data_map: dict[Operation, EditorMetaData] = EditorMetaData.get_editor_metadata_map()
        edited_meta_data: EditorMetaData = meta_data_map.get(Operation.Edited)
        self.assertEqual(Operation.Edited, edited_meta_data.operation_type)
        self.assertEqual("edited_rows", edited_meta_data.operation_key)
        self.assertEqual(dict(), edited_meta_data.default_value)

    def test_deleted_editor_metadata_config(self):
        meta_data_map: dict[Operation, EditorMetaData] = EditorMetaData.get_editor_metadata_map()
        deleted_meta_data: EditorMetaData = meta_data_map.get(Operation.Deleted)
        self.assertEqual(Operation.Deleted, deleted_meta_data.operation_type)
        self.assertEqual("deleted_rows", deleted_meta_data.operation_key)
        self.assertEqual([], deleted_meta_data.default_value)

    def test_get_editor_metadata_map(self):
        meta_data_map: dict[Operation, EditorMetaData] = EditorMetaData.get_editor_metadata_map()
        self.assertEqual(3, len(meta_data_map))
        for operation, meta_data in meta_data_map.items():
            self.assertTrue(isinstance(operation, Operation))
            self.assertTrue(isinstance(meta_data, EditorMetaData))

    def test_get_key_map(self):
        key_map: dict[ModelSessionDataEnum, str] = EditorMetaData.get_key_map("model")
        self.assertEqual([e for e in ModelSessionDataEnum], list(key_map.keys()))
        for e in ModelSessionDataEnum:
            self.assertEqual(["model", e.value], key_map[e].split("|")[:2])

    def test_get_new_key(self):
        self.assertNotEqual(EditorMetaData.get_new_key("key", ModelSessionDataEnum.EditorData),
                            EditorMetaData.get_new_key("key", ModelSessionDataEnum.EditorData))
