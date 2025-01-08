from typing import Optional
import logging
import streamlit as st
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: SecretStr = Field(st.secrets.openai_key, description="OpenAI API Key")
    DEFAULT_LLAMA_CLOUD_API_URL: str = Field("https://api.cloud.llamaindex.ai", description="LlamaCloud API URL")
    DEFAULT_LLAMA_CLOUD_API_KEY: Optional[SecretStr] = Field(None, description="Default LlamaCloud API Key")
    LOG_LEVEL: str = Field("INFO", description="Logging level")

    @field_validator("LOG_LEVEL")
    def validate_log_level(cls, value: str) -> str:
        value = value.upper()
        if not hasattr(logging, value):
            raise ValueError("Invalid log level")
        return value

settings = Settings()
