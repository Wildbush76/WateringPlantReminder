import asyncio
import logging
import time

from bleak import BleakClient

from .server import Server

VALUE_LOG_FILE = "data.csv"

SERVICE_UUID = "2db9dd7d-1637-47db-96d4-495484ed45e7"
CHARACTERISTIC_UUID = "38072c05-608d-441e-987e-69ee78d4a58c"


class logging_server:
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    async def callback(self, device: BleakClient) -> None:
        _bytes = device.read_gatt_char(CHARACTERISTIC_UUID)
        if _bytes is not None:
            reading = int.from_bytes(_bytes, byteorder="little")
            self.save_reading(reading)
        else:
            self._logger.warning(
                f"Failed to read characteristicUUID : {self._settings.characteristicUUID}"
            )

    def save_reading(self, value: int) -> None:
        with open(VALUE_LOG_FILE, "a") as file:
            file.write(f"{time.time()},{value}")

    async def run(self):
        self._logger.info("Starting logging server")

        server = Server(self.callback, CHARACTERISTIC_UUID)

        await server.start()
        await asyncio.Future()
