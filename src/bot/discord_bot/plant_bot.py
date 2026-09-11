import asyncio
import logging
import signal
import time
from typing import override

import aiofiles
import discord
from bleak import BleakClient
from discord.app_commands import Command

from ..util.grapher import create_graph
from ..util.server import Server
from .bot_settings import PlantSettings
from .discord_logger_handler import DiscordHandler


class plant_bot(discord.Client):
    def __init__(self):
        self._settings: PlantSettings = PlantSettings()
        self._ble_server: Server = Server(
            self._device_callback, self._settings.serviceUUID
        )
        self._first_on_ready: bool = True

        # setup logging
        self._logger = logging.getLogger()
        self._logger.addHandler(logging.FileHandler(self._settings.log_file))
        self._discord_logger = DiscordHandler(self, self._settings.owner)
        self._discord_logger.setLevel(logging.ERROR)
        self._logger.addHandler(self._discord_logger)

        # setup discord bot
        discord.VoiceClient.warn_dave = False
        discord.VoiceClient.warn_nacl = False
        intents = discord.Intents.default()
        super().__init__(intents=intents, status=discord.Status.online)

    async def _device_callback(self, device: BleakClient) -> None:
        _bytes = await device.read_gatt_char(self._settings.characteristicUUID)
        if _bytes is not None:
            reading = int.from_bytes(_bytes, byteorder="little")

            asyncio.create_task(self._process_reading(reading))
        else:
            self._logger.warning(
                f"Failed to read characteristicUUID : {self._settings.characteristicUUID}"
            )

    async def _process_reading(self, reading: int):
        await self._log_reading(reading)

    async def _log_reading(self, reading: int):
        async with aiofiles.open(self._settings.data_file, mode="a") as file:
            await file.write(f"{time.time()},{reading}\n")

    def run(self, token: str, *args, **kwargs) -> None:
        super().run(token, *args, **kwargs)

    @override
    async def on_ready(self) -> None:
        self._logger.info(self._logging_header("on_ready Enter"))

        if self._first_on_ready:
            self._first_on_ready = False

            self._logger.info("Starting BLE")
            await self._ble_server.start()

            self._logger.info("Registering Commands")
            await self._register_commands()

            self._logger.info("Setting Up Signal Logger")
            loop = asyncio.get_event_loop()
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(
                    sig, lambda: asyncio.create_task(self.shutdown())
                )

        self._logger.info(self._logging_header("on_ready Exit"))
        self._logger.info("Bot Started")

    def _logging_header(self, message: str) -> str:
        target_length = 40

        dash_count = (target_length - len(message)) // 2
        return "-" * dash_count + message + "-" * dash_count

    async def _register_commands(self):
        # create slash commands
        tree = discord.app_commands.CommandTree(self)

        tree.add_command(
            Command(
                name="create_graph",
                callback=self.graph,
                description="Creates a graph of logged data",
            )
        )

        tree.add_command(
            Command(
                name="log_dump",
                callback=self.log_dump,
                description="Outputs the log file",
            )
        )
        await tree.sync()

    async def shutdown(self):
        self._logger.info("Shutting down")
        await self._discord_logger.info(title="Bot-Status", message="Bot shutting down")
        await self._ble_server.stop()
        await self.close()

    async def graph(self, interaction: discord.Interaction) -> None:
        await self._logger.info("Creating graph")
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

    async def log_dump(self, interaction: discord.Interaction):
        self._logger.info("Dumping logs")
        logs = self._settings.log_file
        if not logs.is_file():
            await interaction.response.send_message("No log file found!")
            self._logger.warning("No log file found")
            return

        file = discord.File(logs)

        await interaction.response.send_message(content="LOGS", file=file)
