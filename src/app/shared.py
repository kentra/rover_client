from app.models.config import AppConfig
from app.hardware.hub_control import HubControl

cfg = AppConfig()  # type: ignore
hub = HubControl(cfg)
