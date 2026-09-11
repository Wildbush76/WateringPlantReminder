import logging
from collections.abc import Awaitable, Callable

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData


class Server:
    async def _ble_detection(
        self, device: BLEDevice, advertisement: AdvertisementData
    ) -> None:
        if not self._scanning:
            return
        await self.stop()

        self._logger.debug(f"Trying to connect to {device.name} @ {device.address}")
        try:
            async with BleakClient(device.address) as client:
                if client.is_connected:
                    self._logger.debug(f"Connected to {device.name}")
                    await self._device_callback(client)

        except Exception as e:
            self._logger.warning("failed to connect to BLE device %s", e, exc_info=True)
        finally:
            await self.start()

    def __init__(
        self,
        device_callback: Callable[[BleakClient], Awaitable],
        *serviceUUIDs: list[str],
    ):
        self._logger = logging.getLogger(__name__)
        self._device_callback = device_callback
        self._scanner = BleakScanner(self._ble_detection, serviceUUIDs, "active")
        self._scanning = False

    async def start(self) -> None:
        if self._scanning:
            return

        self._logger.debug("Starting Scanning BLE")
        self._scanning = True
        await self._scanner.start()

    async def stop(self) -> None:
        if not self._scanning:
            return
        self._logger.debug("Stopping Scanning BLE")
        self._scanning = False
        await self._scanner.stop()
