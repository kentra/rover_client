# import busio
import time
import mmwave_presence as mmwave
from periphery import Serial


uart = Serial(
    "/dev/ttyS4",
    baudrate=115200,
    databits=8,
    parity="none",
    stopbits=1,
    xonxoff=False,
    rtscts=False,
)

mmwave = mmwave.MMWave(uart)

mmwave.set_basic_config(8, 8, presence_timeout=5)
mmwave.set_resolution(75)

while True:
    # update values
    mmwave.read()

    # printing like this is really just for debugging
    print(f"{mmwave}")

    time.sleep(0.1)
