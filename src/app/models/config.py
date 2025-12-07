from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DEVICE_UUID: str
    WRITE_CHAR_UUID: str
    DEADZONE: int
