from ai_code_agent.core import BaseSettings, SettingsConfigDict, Field


class Settings(BaseSettings):
    # FastApi details
    SQL_SERVER_URL: str | None = Field(default=None)
    SECRET_KEY: str = Field(default="")
    ALGORITHM: str | None = Field(default=None)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=0)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=0)
    COOKIE_NAME: str = Field(default="")

    # RAG details
    AZURE_CHAT_API_KEY: str | None = Field(default=None)
    AZURE_CHAT_ENDPOINT: str | None = Field(default=None)
    AZURE_CHAT_DEPLOYMENT: str | None = Field(default=None)
    AZURE_EMBED_API_KEY: str | None = Field(default=None)
    AZURE_EMBED_ENDPOINT: str | None = Field(default=None)
    AZURE_EMBED_DEPLOYMENT: str | None = Field(default=None)
    CHROMA_DIR: str | None = Field(default=None)
    GOOGLE_API_KEY: str | None = Field(default=None)

    model_config = SettingsConfigDict(
        env_ignore_empty=True, env_file=".env", env_file_encoding="utf-8"
    )


settings = Settings()
