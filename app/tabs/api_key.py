import streamlit as st
from app_settings import settings

async def api_key_tab():
    st.write("Enter your API key for LlamaCloud:")
    with st.form(key='api_key_form'):
        if st.session_state.get("llx_base_url") is None:
            st.session_state.llx_base_url = settings.DEFAULT_LLAMA_CLOUD_API_URL
        base_url = st.text_input("Base URL", key="llx_base_url", placeholder=settings.DEFAULT_LLAMA_CLOUD_API_URL)
        default_api_key = settings.DEFAULT_LLAMA_CLOUD_API_KEY.get_secret_value() if settings.DEFAULT_LLAMA_CLOUD_API_KEY else None
        api_key = st.text_input(
            "API Key",
            value=default_api_key,
            type="password",
            key="llx_api_key",
            placeholder="llx-..."
        )
        submit_button = st.form_submit_button(label='Submit')

        if submit_button:
            if not api_key.startswith("llx-"):
                st.error("Invalid API key. Please try again.")
            elif not base_url.startswith("http"):
                st.error("Base URL must start with http. Please try again")
            else:
                st.toast("API Key submitted!")
