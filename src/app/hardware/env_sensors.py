#!/usr/bin/env python

from bme280 import BME280
from smbus import SMBus

from app.models.state_models import (
    EnvironmentSensorsState,
    get_current_cache_state,
)


class EnvironmentSensors:
    """Environment Sensors Class"""

    def __init__(self, bus_number: int) -> None:
        self.bus = SMBus(bus_number)
        self.bme280 = BME280(i2c_dev=self.bus)

    async def get_temperature(self) -> float:
        return self.bme280.get_temperature()

    async def get_humidity(self) -> float:
        return self.bme280.get_humidity()

    async def get_pressure(self) -> float:
        return self.bme280.get_pressure()

    async def get_all(self) -> None:
        current_cache_state = get_current_cache_state()
        current_cache_state.environment_sensors = EnvironmentSensorsState(
            temperature=self.bme280.get_temperature(),
            humidity=self.bme280.get_humidity(),
            pressure=self.bme280.get_pressure(),
        )
