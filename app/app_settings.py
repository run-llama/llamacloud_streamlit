from typing import Optional
import streamlit as st
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: SecretStr = Field(st.secrets.openai_key, description="OpenAI API Key")
    DEFAULT_LLAMA_CLOUD_API_URL: str = Field("https://api.staging.llamaindex.ai", description="LlamaCloud API URL")
    DEFAULT_LLAMA_CLOUD_API_KEY: Optional[SecretStr] = Field(None, description="Default LlamaCloud API Key")

settings = Settings()
