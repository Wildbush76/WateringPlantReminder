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

queue = []


def add_message_to_queue(voice_line: str):
    queue.append(voice_line)


async def send_message(voice_line: str):
    logger.info(f"Sending message {voice_line}")
    if not client.is_ready():
        return
    path = os.path.join(configs.voiceFolder, "funkyTown.ogg")
    if not os.path.isfile(path):
        logger.error(f"Failed to find audio file {voice_line}")
        return

    file = discord.File(path)

    person = await client.fetch_user(configs.vicitim)
    await person.send(voice_line)

server = Server(add_message_to_queue, configs)


@tasks.loop(seconds=20)
async def check_queue():
    logger.info("Checking queue")
    for message in queue:
        await send_message(message)
    queue.clear()


@client.event
async def on_ready():
    await server.start()
    check_queue.start()


token = os.getenv("discord_token")
client.run(token)
