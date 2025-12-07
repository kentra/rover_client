from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # BLE
    BLE_DEVICE_UUID: str
    BLE_WRITE_CHAR_UUID: str
    BLE_DEADZONE: int

    # Environment Sensors
    # BME280
    BME280_I2C_BUS: int
