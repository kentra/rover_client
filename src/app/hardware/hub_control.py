import asyncio
from bleak import BleakClient, BleakScanner, BLEDevice
from app.models.config import AppConfig
from app.models.hub_models import MotorSpeed


class HubControl:
    def __init__(self, cfg: AppConfig) -> None:
        self.cfg: AppConfig = cfg
        self.ble_device: BLEDevice | str | None = None
        self.client: BleakClient | None = None

    def __build_packet(
        self,
        motor_speed: MotorSpeed = MotorSpeed(
            speed_a=0, speed_b=0, speed_c=0, speed_d=0
        ),
    ) -> bytes:
        # Calculate Checksum
        checksum = 0
        # Pydantic model.model_dump() returns a dict of the fields
        for _, value in motor_speed.model_dump().items():
            if value[-1] is not None:
                checksum += value[-1]

        checksum &= 0xFF

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
        """Establishes a persistent connection to the BLE device."""
        if self.client and self.client.is_connected:
            print("# ℹ️ Already connected.")
            return

        print(f"# 🔍 Connecting to {self.cfg.BLE_DEVICE_UUID}...")
        self.client = BleakClient(self.cfg.BLE_DEVICE_UUID)
        
        try:
            await self.client.connect()
            print("# ✅ Connected!")
            # Stop motors initially
            await self.drive_tracks(0, 0)
        except Exception as e:
            print(f"# ❌ Connection failed: {e}")
            self.client = None
            raise e

    async def disconnect(self) -> None:
        if self.client and self.client.is_connected:
            await self.drive_tracks(0, 0) # Safety stop
            await self.client.disconnect()
            print("# 🔌 Disconnected.")
        self.client = None

    async def drive_tracks(self, left: int, right: int) -> None:
        """
        Drive the two tracks.
        Left -> Motor A
        Right -> Motor B
        """
        if not self.client or not self.client.is_connected:
            # print("# ⚠️ Not connected. Ignoring command.")
            return

        # Create packet
        packet = self.__build_packet(
            MotorSpeed(
                speed_a=left, 
                speed_b=right, 
                speed_c=0, 
                speed_d=0
            )
        )

        try:
            await self.client.write_gatt_char(
                self.cfg.BLE_WRITE_CHAR_UUID, packet
            )
        except Exception as e:
            print(f"# ⚠️ Send failed: {e}")
