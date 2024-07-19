from __future__ import annotations

import importlib
import tomllib
from pathlib import Path
from typing import Any, Type, Union, Optional

from base.model import Model
from base.model_list import ModelList
from base.request_handler import RequestHandler
from enums import EndPoint

EXPECTED_CONFIG_DIR = Path(__file__).parent / "configs"


class Config:
    """
    A config class which is expected have to have just one instance across the lifetime of the app
    So, better to call classmethod @get_instance to access the config
    """
    _instance: Optional[Config] = None

    def __init__(self, filepath: Path):
        """ To maintain a single instance across the lifetime of the app, call get_instance instead """

        with filepath.open("rb") as fp:
            self._config = tomllib.load(fp)

        self.name = self._config.get("name", None)
        Config._instance = self

        self.model_class: Type[Model] = self._get_class_impl("model", Model)
        self.model_list_class: Type[ModelList] = self._get_class_impl("model_list", ModelList)
        self.model_audit_class: Type[Model] = self._get_class_impl("model_audit", Model)
        self.request_handler_class: Type[RequestHandler] = self._get_class_impl("request", RequestHandler)

    def get_value(self, key: str) -> Any:
        return self._config.get(key, None)

    @property
    def parsed_config(self) -> dict[str, Any]:
        return self._config

    def override_config(self, config_values: dict[str, Any]) -> None:
        self._config.update(config_values)

    def _get_end_point_impl(self, group: str, end_point: EndPoint) -> str:
        apis_dict: dict[str, Union[str, int]] = self._config["apis"]
        return f'{apis_dict["host"]}:{apis_dict["port"]}{apis_dict[group][end_point.value]}'

    def get_model_audit_end_point(self, end_point: EndPoint) -> str:
        return self._get_end_point_impl("model_audit", end_point)

    def get_model_end_point(self, end_point: EndPoint) -> str:
        return self._get_end_point_impl("model", end_point)

    @classmethod
    def reset_instance(cls):
        cls._instance = None

    @classmethod
    def has_instance(cls) -> bool:
        return cls._instance is not None

    @classmethod
    def get_configs(cls, config_file_dir: Union[Path, str] = EXPECTED_CONFIG_DIR) -> dict[str, Config]:

        if not config_file_dir or not Path(config_file_dir).is_dir():
            raise NotADirectoryError(config_file_dir)

        config_files = Path(config_file_dir).glob("**/*.toml")
        if not config_files:
            raise FileNotFoundError(config_file_dir)

        parsed_configs: list[Config] = [Config(config_file) for config_file in config_files]
        return {config.name: config for config in parsed_configs}

    def _get_class_impl(self, group: str, class_type):
        module = importlib.import_module(self._config[group]["module"])
        model_class: Type[class_type] = getattr(module, self._config[group]["class"])
        if issubclass(model_class, class_type):
            return model_class

        raise TypeError(f'Expected a type (or derived from) [{class_type}] but found: [{model_class}]')

    def __repr__(self):
        return self.name

    def __str__(self):
        return repr(self)


if __name__ == '__main__':
    print(Config.get_configs()["movies"].parsed_config)
