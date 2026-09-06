import asyncio
from logging import Handler, LogRecord
from typing import override

import discord
from discord.embeds import Embed


class DiscordHandler(Handler):
    def __init__(self, discord_client: discord.Client, target_user: int):
        self._client: discord.Client = discord_client
        self._user: int | discord.User = target_user

        super().__init__()

    @override
    def emit(self, record: LogRecord) -> None:
        if not self._client.is_closed():
            asyncio.ensure_future(self._send_message(record))

    async def _send_message(self, record: LogRecord) -> None:
        try:
            if isinstance(self._user, int):
                self._user = await self._client.fetch_user(self._user)

            color = discord.Color.light_gray()

            match record.levelname.upper():
                case "INFO":
                    color = discord.Color.blue()
                case "WARNING":
                    color = discord.Color.yellow()
                case "ERROR":
                    color = discord.Color.red()
                case "CRITICAL":
                    color = discord.Color.dark_red()

            embed = Embed(
                color=color,
                title=f"{record.module}:{record.levelname}",
                description=record.message,
            )
            await self._user.send(embed=embed)
        except Exception as e:  # noqa: BLE001
            print(f"ERROR discordHandler {e}")
