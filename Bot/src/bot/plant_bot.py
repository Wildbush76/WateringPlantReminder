import asyncio
import logging
import time
from typing import override

import aiofiles
import discord
from bleak import BleakClient

from .bot_settings import PlantSettings
from .server import Server


class plant_bot(discord.Client):
    def __init__(self):
        self._settings: PlantSettings = PlantSettings()
        self._ble_server: Server = Server()
        self._logger = logging.getLogger(__name__)

        # setup discord bot
        intents = discord.Intents.default()

        super().__init__(intents=intents)

    async def _device_callback(self, device: BleakClient) -> None:
        _bytes = device.read_gatt_char(self._settings.characteristicUUID)
        if _bytes is not None:
            reading = int.from_bytes(_bytes, byteorder="little")

            asyncio.ensure_future(self._process_reading(reading))
        else:
            self._logger.warning(
                f"Failed to read characteristicUUID : {self._settings.characteristicUUID}"
            )

    async def _process_reading(self, reading: int):
        await self._log_reading(reading)

    async def _log_reading(self, reading: int):
        async with aiofiles.open(self._settings.data_file, mode="a") as file:
            file.write(f"{time.time()},{reading}")

    def run(self) -> None:
        self.run(self._settings.discord_token)

    @override
    async def on_ready(self) -> None:
        await self._ble_server.start()

        self._logger.info(f"{'-' * 10}Bot Started{'-' * 10}")
