import copy
import tomllib
from pathlib import Path

from core.model_config import ModelConfig

PROJECT_ROOT_DIR: Path = Path(__file__).parent
DEFAULT_CONFIG_FILE: Path = PROJECT_ROOT_DIR / 'config.toml'


class Config:
    @classmethod
    def get_model_configs(cls, parent_config_file_path: Path = DEFAULT_CONFIG_FILE) -> dict[str, ModelConfig]:

        if not isinstance(parent_config_file_path, Path):
            raise TypeError(f"'{parent_config_file_path}' [{type(parent_config_file_path)}] is not a Path object")

        if not parent_config_file_path.exists() or not parent_config_file_path.is_file():
            raise FileNotFoundError(f"'{parent_config_file_path}' file does not exist")

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

        return model_configs


def main():
    configs: dict[str, ModelConfig] = Config.get_model_configs()
    print(configs)


if __name__ == '__main__':
    main()
