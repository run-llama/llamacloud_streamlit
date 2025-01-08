import asyncio
from collections import OrderedDict
from typing import Callable, Coroutine, Dict
import logging
import streamlit as st
from app_settings import settings
from tabs.api_key import api_key_tab
from tabs.indices import indices_tab
from tabs.composite_retriever import composite_retriever_tab
from tabs.chat import chat_tab

TABS_DICT: Dict[str, Callable[..., Coroutine]] = OrderedDict([
    ("API Key", api_key_tab),
    ("Indices", indices_tab),
    ("Composite Retriever", composite_retriever_tab),
    ("Chat", chat_tab),
])

def setup_logging():
    log_level = getattr(logging, settings.LOG_LEVEL)
    logging.basicConfig(
        format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=log_level
    )


async def main():
    setup_logging()
    st.set_page_config(page_title="LlamaCloud App", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)

    tabs = st.tabs(TABS_DICT.keys())

    for tab_name, tab in zip(TABS_DICT.keys(), tabs):
        with tab:
            await TABS_DICT[tab_name]()

if __name__ == "__main__":
    asyncio.run(main())
