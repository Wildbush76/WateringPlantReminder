import time
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
import asyncio
import logging


LOG_FILE = "log.csv"
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Server:
    async def _ble_detection(self, device: BLEDevice, advertisement: AdvertisementData):
        if device in self.connections:
            return
        self.connections.add(device)
        self.logger.info(
            f"Trying to connect to {device.name} @ {device.address}")
        await self.scanner.stop()
        try:
            async with BleakClient(device.address) as client:
                if (client.is_connected):
                    self.logger.info(
                        f"Connected to device {client.name} @ {client.address}")
                    result = await client.read_gatt_char(self.characteristic_uuid)

                    if (result is not None):
                        reading = int.from_bytes(result, byteorder="little")
                        await self._proccess_reading(reading)
                    else:
                        self.logger.warning("Failed to read")
        except OSError as e:
            self.logger.error(e)
        finally:
            self.logger.info("Removing connection")
            self.connections.remove(device)
            self.logger.info("Resuming scanning")
            asyncio.create_task(self.scanner.start())

    async def _proccess_reading(self, raw_reading: int):
        with open(self.log_file, "a") as file:
            current_time = int(time.time())
            file.write(f"{current_time},{raw_reading}\n")

    def __init__(self, service_uuid: str, characteristic_uuid: str, log_file: str):
        self.logger = logging.getLogger(__name__)
        self.connections = set()
        self.scanner = BleakScanner(
            self._ble_detection, [service_uuid], 'active')
        self.characteristic_uuid = characteristic_uuid
        self.log_file = log_file

    async def start(self):
        self.logger.info("starting BLE")
        asyncio.create_task(self.scanner.start())


async def main():
    server = Server("2db9dd7d-1637-47db-96d4-495484ed45e7",
                    "38072c05-608d-441e-987e-69ee78d4a58c", "readings.csv")
    await server.start()
    await asyncio.Future()
asyncio.run(main())
