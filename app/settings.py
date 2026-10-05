from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    KAI_API_KEY: SecretStr
    OPENAI_API_KEY: SecretStr
    REDIS_URL: SecretStr

settings = Settings()