from typing import Union

from fastapi import FastAPI
from app.routers import state
from app.routers import web_socket
from app.routers import movement
from app.models.config import AppConfig
from app.hardware.env_sensors import EnvironmentSensors


cfg = AppConfig()  # type: ignore
app = FastAPI()
env_sensors = EnvironmentSensors(bus_number=cfg.BME280_I2C_BUS)


app.include_router(state.router)
app.include_router(web_socket.router)
app.include_router(movement.router)
