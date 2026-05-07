import discord
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

import os
import json


async def loadConfigs(filename: str) -> dict:
    configs = {}
    if os.path.isfile(filename):
        with open(filename, "r") as file:
            configs = json.load(file)
    else:
        raise FileNotFoundError("Failed to load configs")

    return configs


intents = discord.Intents.dm_messages
client = discord.Client(intents=intents)


token = os.getenv("plant_token")
client.start(token)
