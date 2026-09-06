import asyncio
import logging
import time
from typing import override

import aiofiles
import discord
from bleak import BleakClient
from discord.app_commands import Command

from .bot_settings import PlantSettings
from .grapher import create_graph
from .server import Server


class plant_bot(discord.Client):
    def __init__(self):
        self._settings: PlantSettings = PlantSettings()
        self._ble_server: Server = Server(
            self._device_callback, self._settings.serviceUUID
        )
        self._logger = logging.getLogger()

        # setup discord bot
        intents = discord.Intents.default()

        super().__init__(intents=intents)

    async def _device_callback(self, device: BleakClient) -> None:
        _bytes = await device.read_gatt_char(self._settings.characteristicUUID)
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
            await file.write(f"{time.time()},{reading}\n")

    def run(self, *args, **kwargs) -> None:
        super().run(self._settings.discord_token, *args, **kwargs)

    @override
    async def on_ready(self) -> None:
        await self._ble_server.start()

        # create slash commands
        tree = discord.app_commands.CommandTree(self)
        tree.add_command(
            Command(
                name="create_graph",
                callback=self.graph,
                description="Creates a graph of logged data",
            )
        )
        await tree.sync()

        self._logger.info(f"{'-' * 10}Bot Started{'-' * 10}")

    async def graph(self, interaction: discord.Interaction) -> None:
        # embed.set_image
        graph = await create_graph(self._settings.data_file)

        if graph is None:
            await interaction.response.send_message("Failed to make graph")
            return

        file = discord.File(fp=graph, filename="graph.png")

        embed = discord.embeds.Embed(
            colour=discord.Color.dark_green(), title="Plant Graph"
        )

        embed.set_image(url="attachment://graph.png")

        await interaction.response.send_message(embed=embed, file=file)
