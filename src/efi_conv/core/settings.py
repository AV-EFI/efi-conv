from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix=f"{__package__}_")

    line_limit: int = 250
    text_limit: int = 8192


settings = Settings()
