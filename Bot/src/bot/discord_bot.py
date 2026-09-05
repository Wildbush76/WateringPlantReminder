import logging
import os
import time
from typing import override

import aiofiles
import discord
from bleak import BleakClient
from discord.ext import tasks

from .bot_settings import PlantSettings
from .server import Server

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


intents = discord.Intents.default()
client = discord.Client(intents=intents)
configs = PlantSettings("configs.json")

queue = []


def add_message_to_queue(voice_line: str):
    queue.append(voice_line)


async def send_message(voice_line: str):
    logger.info(f"Sending message {voice_line}")
    if not client.is_ready():
        return
    path = os.path.join(configs.voice_line_folder, "funkyTown.ogg")
    if not os.path.isfile(path):
        logger.error(f"Failed to find audio file {voice_line}")
        return

    file = discord.File(path)

    person = await client.fetch_user(configs.target_user)
    await person.send(voice_line)


server = Server(add_message_to_queue, configs)


@tasks.loop(seconds=1)
async def check_queue():
    for message in queue:
        logger.info("Sending message")
        await send_message(message)
    queue.clear()


@client.event
async def on_ready():
    await server.start()
    check_queue.start()


token = os.getenv("plant_token")
client.run(token)


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
            await self._process_reading(reading)
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
