from typing import Sequence, Optional, List
from llama_cloud.client import AsyncLlamaCloud
from llama_cloud.types import ProjectCreate, Project
import streamlit as st

DEFAULT_STREAMLIT_PROJECT_NAME = "Streamlit Project"

def check_session_state_keys_populated(required_state_keys: Sequence[str]) -> bool:
    return all(st.session_state.get(key) for key in required_state_keys)


def get_llamacloud_client() -> Optional[AsyncLlamaCloud]:
    if not check_session_state_keys_populated(["llx_base_url", "llx_api_key"]):
        return None
    return AsyncLlamaCloud(base_url=st.session_state.llx_base_url, token=st.session_state.llx_api_key)

async def get_project_selector(client: AsyncLlamaCloud, key_suffix: str, default_project_name: str = DEFAULT_STREAMLIT_PROJECT_NAME) -> Project:
    default_project = await client.projects.upsert_project(request=ProjectCreate(name=default_project_name))
    st.session_state.project_id = st.session_state.get("project_id", default_project.id)
    projects: List[Project] = await client.projects.list_projects(organization_id=default_project.organization_id)
    projects = sorted(projects, key=lambda p: p.name)
    default_project_idx = next((i for i, p in enumerate(projects) if p.id == st.session_state.project_id), 0)
    selected_project = st.selectbox("Select Project",
                                    projects,
                                    key=f"project_selector_{key_suffix}",
                                    index=default_project_idx,
                                    format_func=lambda p: p.name)
    st.session_state.project_id = selected_project.id
    return selected_project