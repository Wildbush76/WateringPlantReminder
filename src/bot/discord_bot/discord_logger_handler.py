import asyncio
from logging import Handler, LogRecord
from typing import override

import discord
from discord.embeds import Embed


class DiscordHandler(Handler):
    def __init__(self, discord_client: discord.Client, target_user: int):
        self._client: discord.Client = discord_client
        self._target_id: int | discord.User = target_user

        super().__init__()

    @override
    def emit(self, record: LogRecord) -> None:
        if not self._client.is_closed():
            asyncio.create_task(self._send_record(record))

    async def _send_message(self, title: str, message: str, color: discord.Color):
        if self._client.is_closed():
            return

        try:
            if isinstance(self._target_id, int):
                self._target_id = await self._client.fetch_user(self._target_id)

            embed = Embed(
                color=color,
                title=title,
                description=message,
            )

            await self._target_id.send(embed=embed)

        except Exception as e:  # noqa: BLE001
            print(f"ERROR-discordHandler {e}")  # logging isnt working so have to print

    async def info(self, title: str, message: str):
        await self._send_message(title, message, discord.Color.blue())

    async def warning(self, title: str, message: str):
        await self._send_message(title, message, discord.Color.yellow())

    async def error(self, title: str, message: str):
        await self._send_message(title, message, discord.Color.red())

    async def critical(self, title: str, message: str):
        await self._send_message(title, message, discord.Color.dark_red())

    async def _send_record(self, record: LogRecord) -> None:

        title = f"{record.module}:{record.levelname}"
        description = record.message

        match record.levelname.upper():
            case "INFO":
                await self.info(title, description)
            case "WARNING":
                await self.warning(title, description)
            case "ERROR":
                description += f" -> {record.exc_text}"
                await self.error(title, description)
            case "CRITICAL":
                description += f" -> {record.exc_text}"
                await self.critical(title, description)
