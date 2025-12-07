import time
import mmwave_presence as mmwave
from periphery import Serial


class MMWave:
    def __init__(self, port: int, baud_rate: int) -> None:
        """Class for mmWave."""
        self.uart = Serial(
            "/dev/ttyS4",
            baudrate=115200,
            databits=8,
            parity="none",
            stopbits=1,
            xonxoff=False,
            rtscts=False,
        )

        # Set up mmwave object
        self.mmwave = mmwave.MMWave(self.uart)
        self.mmwave.set_basic_config(8, 8, presence_timeout=5)
        self.mmwave.set_resolution(75)
