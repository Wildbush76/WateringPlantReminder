import asyncio
import logging
from collections.abc import Awaitable, Callable

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData


class Server:
    async def _ble_detection(
        self, device: BLEDevice, advertisement: AdvertisementData
    ) -> None:
        if device in self._connections:
            return

        self._connections.add(device)
        self._logger.info(f"Trying to connect to {device.name} @ {device.address}")
        try:
            async with BleakClient(device.address) as client:
                if client.is_connected:
                    self._logger.info(
                        f"Connected to device {client.name} @ {client.address}"
                    )
                    try:
                        await self._device_callback(client)
                    finally:
                        self._connections.remove(device)

        except OSError as e:
            self._logger.error(e)
        finally:
            self._connections.remove(device)

    def __init__(
        self,
        device_callback: Callable[[BleakClient], Awaitable],
        *serviceUUIDs: list[str],
    ):
        self._logger = logging.getLogger(__name__)
        self._device_callback = device_callback
        self._connections = set()
        self._scanner = BleakScanner(self._ble_detection, serviceUUIDs, "passive")
        self.__scanner_task: None | asyncio.Task = None

    async def start(self) -> None:
        self._logger.info("Starting BLE")
        self.__scanner_task = self._scanner.start()

    async def stop(self) -> None:
        if self.__scanner_task is not None:
            self.__scanner_task.cancel()
            await self.__scanner_task
