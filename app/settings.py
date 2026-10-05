from pydantic import Field, SecretStr
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
    TRUST_RAILWAY_PROXY: bool = False
    QUERY_REQUESTS_PER_MINUTE: int = Field(default=5, gt=0)
    TOTAL_QUERY_REQUESTS_PER_DAY: int = Field(default=30, gt=0)

settings = Settings()
