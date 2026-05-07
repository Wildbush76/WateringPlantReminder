import discord
from discord.ext import tasks
import os
from Server import Server
from PlantConfigs import PlantConfigs
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


intents = discord.Intents.default()
client = discord.Client(intents=intents)
configs = PlantConfigs("configs.json")


async def send_message(voice_line: str):
    if not client.is_ready():
        return
    path = os.path.join(configs.voiceFolder, "funkyTown.ogg")
    if not os.path.isfile(path):
        logger.error(f"Failed to find audio file {voice_line}")
        return
    with open(path) as f:
        file = discord.File(f, voice_line)

    person = await client.fetch_user(configs.vicitim)
    await person.send(File=file)

server = Server(send_message, configs)


@client.event
async def on_ready():
    logger.info("READDDDYpy")
    await server.start()


token = os.getenv("discord_token")
client.run(token)
