from __future__ import annotations

import importlib
import tomllib
from pathlib import Path
from typing import Any, Type, Union, Optional

from base.model import Model
from base.model_list import ModelList
from base.request_handler import RequestHandler
from core.singleton import Singleton
from enums import EndPoint

EXPECTED_CONFIG_FILEPATH = Path(__file__).parent / "app_config.toml"


class Config(Singleton):
    """
    A config class which is expected have to have just one instance across the lifetime of the app
    So, better to call classmethod @get_instance to access the config
    """
    _instance: Optional[Config] = None

    def __init__(self, filepath: Path):
        """ To maintain a single instance across the lifetime of the app, call get_instance instead """
        super().__init__()

        with filepath.open("rb") as fp:
            self._config = tomllib.load(fp)

    def get_value(self, key: str) -> Any:
        return self._config.get(key, None)

    def get_parsed_config(self) -> dict[str, Any]:
        return self._config

    def override_config(self, config_values: dict[str, Any]) -> None:
        self._config.update(config_values)

    def _get_end_point_impl(self, group: str, end_point: EndPoint) -> str:
        apis_dict: dict[str, Union[str, int]] = self._config["apis"]
        return f'{apis_dict["host"]}:{apis_dict["port"]}{apis_dict[group][end_point.value]}'

    def get_model_audit_end_point(self, end_point: EndPoint) -> str:
        return self._get_end_point_impl("movies_audit", end_point)

    def get_model_end_point(self, end_point: EndPoint) -> str:
        return self._get_end_point_impl("movies", end_point)

    def get_model_class(self) -> Type[Model]:
        return self._get_class_impl("model", Model)

    def get_model_list_class(self) -> Type[ModelList]:
        return self._get_class_impl("model_list", ModelList)

    def get_model_audit_class(self) -> Type[Model]:
        return self._get_class_impl("model_audit", Model)

    def get_request_handler_class(self) -> Type[RequestHandler]:
        return self._get_class_impl("request", RequestHandler)

    @classmethod
    def get_instance(cls, config_file_path: Optional[Union[Path, str]] = None) -> Config:
        """
        It is optional to pass `config_file_path`. if it is `None`:
         - existing instance will be returned
         - in case, there is no instance, it will fall back to `EXPECTED_CONFIG_FILEPATH`
        :param config_file_path: A `Path` or `str` object representing the object
        :return: `Config` object
        """

        if config_file_path:  # if path is provided, new instance must always be created
            # After validation, it can only be an instance of Path class
            config_file_path: Path = Config._validate_file_path(config_file_path)

            Config.reset_instance()  # if the instance already existed, initializer will raise exception
            return Config(config_file_path)

        if cls._instance is None:
            cls._instance = Config(EXPECTED_CONFIG_FILEPATH)

        return cls._instance

    @staticmethod
    def _validate_file_path(filepath: Union[Path, str]) -> Path:
        """ Validates and returns a valid file path """

        if not isinstance(filepath, Path) and not isinstance(filepath, str):
            raise TypeError('filepath must be a Path object (or string which represents the Path)')

        if isinstance(filepath, str):
            filepath = Path(filepath)

        if not filepath.is_file():
            raise FileNotFoundError(f'Config file [{filepath}] does not exist')

        return filepath

    def _get_class_impl(self, group: str, class_type):
        module = importlib.import_module(self._config[group]["module"])
        model_class: Type[class_type] = getattr(module, self._config[group]["class"])
        if issubclass(model_class, class_type):
            return model_class

        raise TypeError(f'Expected a type (or derived from) [{class_type}] but found: [{model_class}]')


if __name__ == '__main__':
    config_instance = Config(EXPECTED_CONFIG_FILEPATH)
    print(f'Get end point: {config_instance.get_model_end_point(EndPoint.Get)}')
    print(f'Model class: {config_instance.get_model_class()}')
    print(f'Model list class: {config_instance.get_model_list_class()}')
    print(f'Model audit class: {config_instance.get_model_audit_class()}')
    print(f'More about base class: {config_instance.get_model_class().model_fields}')
    print(f'Testing instance by id: {Config.get_instance() is config_instance}')
    # Config(None)  # must throw
