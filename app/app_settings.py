import streamlit as st
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: SecretStr = Field(st.secrets.openai_key, description="OpenAI API Key")
    DEFAULT_LLAMA_CLOUD_API_URL: str = Field("https://api.cloud.llamaindex.ai", description="LlamaCloud API URL")

settings = Settings()
