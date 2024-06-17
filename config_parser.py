import tomllib
from pathlib import Path
from typing import Any, Type, Union

from enums import EndPoint
from pydantic import BaseModel
import importlib

from model_list import ModelList

expected_config_filepath = Path(__file__).parent / "config.toml"


class ConfigParser:
    def __init__(self, filepath: Path = expected_config_filepath):
        with filepath.open("rb") as fp:
            self._config = tomllib.load(fp)

    def get_parsed_config(self) -> dict[str, Any]:
        return self._config

    def get_end_point(self, end_point: EndPoint) -> str:
        return f'{self._config["host"]}:{self._config["port"]}{self._config["apis"][end_point.value]}'

    def _get_class_impl(self, class_name: str) -> Union[Type[BaseModel], Type[ModelList]]:
        module = importlib.import_module(self._config["model_module"])
        model_class: Type[BaseModel] = getattr(module, self._config[class_name])
        if issubclass(model_class, BaseModel):
            return model_class

        raise TypeError(f'Expected a type derived from BaseModel but found: {model_class}')

    def get_model_class(self) -> Type[BaseModel]:
        return self._get_class_impl("model_class")

    def get_model_list_class(self) -> Type[ModelList]:
        return self._get_class_impl("model_list_class")


if __name__ == '__main__':
    config = ConfigParser()
    print(f'Get end point: {config.get_end_point(EndPoint.Get)}')
    print(f'Model class: {config.get_model_class()}')
    print(f'More about model class: {config.get_model_class().model_fields}')
