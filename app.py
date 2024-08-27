import streamlit as st

from core.model_config import ModelConfig
from core.session_data_mgr import SessionDataMgr
from config_parser import ConfigParser

st.set_page_config(layout='wide', initial_sidebar_state="expanded")
configs: dict[str, ModelConfig] = ConfigParser.get_model_configs()

# to create app level instance for all models, once created, rest of the app does not need to pass models
SessionDataMgr.get_instance(models=[m for m in configs.keys()])
pages = {
    "Movies": [
        st.Page("nav_pages/movies/data.py", title="Data", url_path="movies-data"),
        st.Page("nav_pages/movies/audit.py", title="Audit", url_path="movies-audit"),
    ],

    "Super Heros": [
        st.Page("nav_pages/super_heros/data.py", title="Data", url_path="super_heros-data"),
        st.Page("nav_pages/super_heros/audit.py", title="Audit", url_path="super_heros-audit"),
    ]
}

pg = st.navigation(pages)
pg.run()
