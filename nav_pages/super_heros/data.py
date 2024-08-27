from config_parser import ConfigParser
from core.model_config import ModelConfig
from nav_pages.page_util import PageUtil

configs: dict[str, ModelConfig] = ConfigParser.get_model_configs()
PageUtil.update_table_view(configs["super_hero"])
