#!/usr/bin/env python

try:
    from bme280 import BME280
    from smbus import SMBus
    MOCK_SENSORS = False
except (ImportError, ModuleNotFoundError):
    print("⚠️ SMBus/BME280 not found. Using Mock Environment Sensors.")
    MOCK_SENSORS = True
    class SMBus:
        def __init__(self, bus): pass
    class BME280:
        def __init__(self, i2c_dev): pass
        def get_temperature(self): return 25.0
        def get_humidity(self): return 50.0
        def get_pressure(self): return 1013.25


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

