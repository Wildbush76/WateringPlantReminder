from PlantConfigs import PlantConfigs
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from PlantState import PlantState, FreshyHydrated
import asyncio
import logging


class Server:
    async def _ble_detection(self, device: BLEDevice, advertisement: AdvertisementData):
        self.logger.info("BLE detected")
        if device in self.connections:
            return
        self.connections.add(device)
        self.logger.info(
            f"Trying to connect to {device.name} @ {device.address}")
        async with BleakClient(device.address) as client:
            if (client.is_connected):
                self.logger.info(
                    f"Connected to device {client.name} @ {client.address}")
                result = await client.read_gatt_char(self.configs.characteristicUUID)

                if (result is not None):
                    reading = int.from_bytes(result)
                    self.logger.info(f"Reading {reading}")
                    await self._proccess_reading(reading)

                else:
                    self.logger.warning("Failed to read")
        self.connections.remove(device)

    async def _normalize_reading(self, reading: int) -> float:
        return reading / (1 << 12)

    async def _proccess_reading(self, raw_reading: int):
        normalized = await self._normalize_reading(raw_reading)
        delta = self.previous_read - normalized
        self.previous_read = normalized
        self.plant_state = await self.plant_state.RecieveMeasurement(
            normalized, delta)

    def __init__(self, message_callback, configs: PlantConfigs):
        self.logger = logging.getLogger(__name__)
        self.configs = configs
        self.connections = set()
        self.previous_read = 0
        self.plant_state = FreshyHydrated(message_callback)
        self.scanner = BleakScanner(
            self._ble_detection, [configs.serviceUUID], 'passive')

    async def start(self):
        self.logger.info("Starting BLE")
        asyncio.create_task(self.scanner.start())
