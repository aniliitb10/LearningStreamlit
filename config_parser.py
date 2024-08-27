import copy
import tomllib
from pathlib import Path

from streamlit.logger import get_logger

from core.model_config import ModelConfig
from util import Util

PROJECT_ROOT_DIR: Path = Path(__file__).parent
DEFAULT_CONFIG_FILE: Path = PROJECT_ROOT_DIR / 'config.toml'

logger = get_logger(__name__.split('.')[-1])


class ConfigParser:
    """
    The class parses the config and acts as a singleton to get parsed configs
    By default, the configs are loaded from the config.toml located in the project root directory.
    if @get_model_configs method is called, it will check if that file is already read
    -  if yes: then parse the configs will be returned
    -  if no: then file will be parsed, and then the newly parsed configs will be returned

    There is a helper method supported to reset the read configs
    """
    configs: dict[str, ModelConfig] | None = None
    config_file_path: Path | None = None

    @classmethod
    def get_model_configs(cls, parent_config_file_path: Path = DEFAULT_CONFIG_FILE) -> dict[str, ModelConfig]:
        if cls.configs is not None and cls.config_file_path == parent_config_file_path:
            return cls.configs

        logger.info(f'Reading config from {parent_config_file_path}')

        Util.file_must_exist(parent_config_file_path)

        with parent_config_file_path.open("rb") as config_file:
            config: dict = tomllib.load(config_file)

        child_config_directory: Path = PROJECT_ROOT_DIR / config.get("child_config_directory")
        if not child_config_directory.exists() or not child_config_directory.is_dir():
            raise NotADirectoryError(f"'{child_config_directory}' is not a directory")

        model_configs: dict[str, ModelConfig] = {}
        for child_config_file in config.get("child_configs"):
            child_config_full_path = child_config_directory / child_config_file
            model_config: ModelConfig = ModelConfig(child_config_full_path,
                                                    copy.deepcopy(config.get("common_config", dict())))
            model_configs[model_config.name] = model_config

        if not model_configs:
            raise RuntimeError(f"No child configs found in '{child_config_directory}'")

        cls.configs = model_configs
        cls.config_file_path = parent_config_file_path
        return model_configs

    @classmethod
    def reset_configs(cls):
        cls.configs = None
        cls.config_file_path = None
