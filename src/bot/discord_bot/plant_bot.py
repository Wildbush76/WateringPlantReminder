from __future__ import annotations

import asyncio
import logging
import signal
import time
from pathlib import Path
from typing import override

import aiofiles
import discord
from bleak import BleakClient
from discord.app_commands import Command
from discord.ext import tasks

from ..util.grapher import create_graph
from ..util.server import Server
from .bot_settings import PlantSettings
from .discord_logger_handler import DiscordHandler


async def _owner_only(self, func: callable[(plant_bot, discord.Interaction), None]):
    def wrapper(self: plant_bot, interaction: discord.Interaction):
        if interaction.user.id == self._settings.owner:
            func(self, interaction)
        else:
            self._logger.warning(
                f"Unauthorized user {interaction.user.name} attempting to run command: {func.__name__} "
            )


class plant_bot(discord.Client):
    def __init__(self):
        self._settings: PlantSettings = PlantSettings()
        self._ble_server: Server = Server(
            self._device_callback, self._settings.serviceUUID
        )
        self._first_on_ready: bool = True
        self._last_read_time: float = time.time()
        self._PROBE_WARN_TIME = 60 * 60  # Warn if we haven't got a reading in an hour
        self._tasks: list[tasks.Loop] = []

        # setup logging
        self._logger = logging.getLogger()
        log_format = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = logging.FileHandler(self._settings.log_file)
        file_handler.setFormatter(log_format)
        self._logger.addHandler(file_handler)
        self._discord_logger = DiscordHandler(self, self._settings.owner)
        self._discord_logger.setLevel(logging.ERROR)
        self._discord_logger.setFormatter(log_format)
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
        self._last_read_time = time.time()
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

            self._logger.info("Start tasks")
            await self._setup_tasks()

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
                callback=self._create_graph,
                description="Creates a graph of logged data",
            )
        )

        tree.add_command(
            Command(
                name="log_dump",
                callback=self._log_dump,
                description="Outputs the log file",
            )
        )

        tree.add_command(
            Command(
                name="clear_logs",
                callback=self._clear_logs,
                description="Clears the log file",
            )
        )

        tree.add_command(
            Command(
                name="clear_data",
                callback=self._clear_data,
                description="Clears the data file",
            )
        )
        await tree.sync()

    async def _setup_tasks(self):
        self._tasks.append(
            tasks.Loop(
                self._check_probe_alive,
                seconds=0,
                minutes=0,
                hours=1,
                time=discord.utils.MISSING,
                count=None,
                reconnect=True,
                name=None,
            )
        )

        for task in self._tasks:
            task.start()

    async def shutdown(self):
        self._logger.info("Shutting down")
        await self._discord_logger.info(title="Bot-Status", message="Bot shutting down")
        await self._ble_server.stop()

        for task in self._tasks:
            task.stop()

        await self.close()

    async def _check_probe_alive(self):
        time_since = time.time() - self._last_read_time

        if time_since > self._PROBE_WARN_TIME:
            await self._discord_logger.warning(
                title="PROBE TIMEOUT",
                message=f"It has been {time_since}s since a reading from the probe. Its battery may be dead",
            )

    # ---------------------Commands--------------------

    async def _create_graph(self, interaction: discord.Interaction) -> None:
        self._logger.info("Creating graph")
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

    async def _send_file(
        self, interaction: discord.Interaction, file: Path, message: str = None
    ):
        if file.is_file():
            await interaction.response.send_message(f"File: {file.name} not found!")
            self._logger.warning(f"Send-File: Failed to file file: {file.name}")
            return
        file = discord.File(file)
        await interaction.response.send_message(content=message, file=file)

    @_owner_only
    async def _data_dump(self, interaction: discord.Interaction):
        self._logger.info("Dumping data")
        self._send_file(interaction, self._settings.data_file, "Data file")

    @_owner_only
    async def _log_dump(self, interaction: discord.Interaction):
        self._logger.info("Dumping logs")
        self._send_file(interaction, self._settings.log_file, "Log file")

    @_owner_only
    async def _clear_logs(self, interaction: discord.Interaction):
        if self._settings.log_file.is_file():
            self._settings.log_file.unlink()
            await interaction.response.send_message(content="Logs cleared")
        else:
            await interaction.response.send_message("No logs found")
        self._logger.info("Clearing logs")

    @_owner_only
    async def _clear_data(self, interaction: discord.Interaction):
        if self._settings.data_file.is_file():
            self._settings.data_file.unlink()
            await interaction.response.send_message(content="Data cleared")
        else:
            await interaction.response.send_message("No data file found")
        self._logger.info("Clearing data")
