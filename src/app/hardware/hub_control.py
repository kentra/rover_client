import asyncio
from bleak import BleakClient, BleakScanner, BLEDevice
from app.models.config import AppConfig
from app.models.hub_models import MotorSpeed


class HubControl:
    def __init__(self, cfg: AppConfig) -> None:
        self.cfg: AppConfig = cfg
        self.ble_device: BLEDevice | str | None = None

    def __build_packet(
        self,
        motor_speed: MotorSpeed = MotorSpeed(
            speed_a=0, speed_b=0, speed_c=0, speed_d=0
        ),
    ) -> bytes:
        # Calculate Checksum
        checksum = 0
        # Pydantic model.model_dump() returns a dict of the fields
        # The values are already mapped to signed bytes by the validator
        print(motor_speed.model_dump())
        for _, value in motor_speed.model_dump().items():
            if value[-1] is not None:
                checksum += value[-1]
        print(f"Checksum pre byte: {checksum}")
        checksum &= 0xFF
        print(f"Checksum pre byte: {checksum}")

        # Header AB CD 01 ...
        return bytes(
            [
                0xAB,
                0xCD,
                0x01,
                motor_speed.speed_a[-1],  # type: ignore
                motor_speed.speed_b[-1],  # type: ignore
                motor_speed.speed_c[-1],  # type: ignore
                motor_speed.speed_d[-1],  # type: ignore
                checksum,
            ]
        )

    async def connect(self) -> None:
        if not self.ble_device:
            self.ble_device = self.cfg.DEVICE_UUID
        async with BleakClient(address_or_ble_device=self.ble_device) as client:  # type: ignore
            print("# ✅ Connected!")
            # Stopping first (sending 0x00)...
            await client.write_gatt_char(
                self.cfg.WRITE_CHAR_UUID, data=self.__build_packet()
            )
            await asyncio.sleep(delay=1)

    async def locate_device(self) -> None:
        await BleakScanner.find_device_by_address(
            device_identifier=self.cfg.DEVICE_UUID, timeout=10.0
        )
        await asyncio.sleep(delay=0.1)

    async def run_smooth(
        self,
        motor_speed: MotorSpeed = MotorSpeed(
            speed_a=0, speed_b=0, speed_c=0, speed_d=0
        ),
        delay: float = 0.1,
    ) -> None:
        """Ramps up the motors for smoother trhottle

        Args:
            motor_speed (MotorSpeed, optional): _description_. Defaults to MotorSpeed( speed_a=0, speed_b=0, speed_c=0, speed_d=0 ).
            delay (float, optional): _description_. Defaults to 0.1.
        """

        # 🚀 Ramping UP Forward (0 -> 100%)...
        async with BleakClient(address_or_ble_device=self.ble_device) as client:  # type: ignore
            for s in range(0, 101, 5):
                print(f"   Speed: {s}%")
                await client.write_gatt_char(
                    char_specifier=self.cfg.WRITE_CHAR_UUID,
                    data=self.__build_packet(
                        motor_speed=MotorSpeed(
                            speed_a=s, speed_b=0, speed_c=0, speed_d=0
                        )
                    ),
                )
                await asyncio.sleep(delay=delay)

    async def run(
        self,
        motor_speed: MotorSpeed = MotorSpeed(
            speed_a=0, speed_b=0, speed_c=0, speed_d=0
        ),
        duration: float = 0.1,
    ) -> None:
        async with BleakClient(address_or_ble_device=self.ble_device) as client:  # type: ignore
            await client.write_gatt_char(
                char_specifier=self.cfg.WRITE_CHAR_UUID,
                data=self.__build_packet(motor_speed=motor_speed),
            )
            await asyncio.sleep(delay=duration)
