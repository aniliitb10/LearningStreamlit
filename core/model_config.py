from __future__ import annotations

import importlib
import tomllib
from pathlib import Path
from typing import Any, Type, Union

from base.model import Model
from base.model_list import ModelList
from base.request_handler import RequestHandler
from enums import EndPoint


class ModelConfig:
    """
    A config class which is expected have to all the config details for a particular model.
    - if there are multiple models, then there is expected to be multiple instances of this class
    """

    def __init__(self, filepath: Path, base_config: dict):
        """ To maintain a single instance across the lifetime of the app, call get_instance instead """
        self.config = base_config if isinstance(base_config, dict) and base_config else {}

        if not isinstance(filepath, Path):
            raise TypeError(f'"{filepath}" [{type(filepath)}] must be a Path object')

        if not filepath.exists() or not filepath.is_file():
            raise FileNotFoundError(f'"{filepath}" does not exist')

        with filepath.open("rb") as fp:
            self.config.update(tomllib.load(fp))

        self.name = self.config.get("name", None)

        self.model_class: Type[Model] = self._get_class_impl("model", Model)
        self.model_list_class: Type[ModelList] = self._get_class_impl("model_list", ModelList)
        self.model_audit_class: Type[Model] = self._get_class_impl("model_audit", Model)
        self.request_handler_class: Type[RequestHandler] = self._get_class_impl("request", RequestHandler)
        self.host: str = self.config["apis"]["host"]
        self.port: int = self.config["apis"]["port"]

    def get_value(self, key: str) -> Any:
        return self.config.get(key, None)

    def _get_end_point_impl(self, group: str, end_point: EndPoint) -> str:
        apis_dict: dict[str, Union[str, int]] = self.config["apis"]
        return f'{self.host}:{self.port}{apis_dict[group][end_point.value]}'

    def get_model_audit_end_point(self, end_point: EndPoint) -> str:
        return self._get_end_point_impl("model_audit", end_point)

    def get_model_end_point(self, end_point: EndPoint) -> str:
        return self._get_end_point_impl("model", end_point)

    def _get_class_impl(self, group: str, class_type):
        module = importlib.import_module(self.config[group]["module"])
        model_class: Type[class_type] = getattr(module, self.config[group]["class"])
        if issubclass(model_class, class_type):
            return model_class

        raise TypeError(f'Expected a type (or derived from) [{class_type}] but found: [{model_class}]')

    def __repr__(self):
        return self.name

    def __str__(self):
        return repr(self)
