import asyncio
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

connections = set()


async def Callback(device: BLEDevice, data: AdvertisementData):
    if device in connections:
        return
    print(device.name)
    connections.add(device)
    async with BleakClient(device.address) as client:
        print(client.is_connected)
        if (client.is_connected):
            result = await client.read_gatt_char("38072c05-608d-441e-987e-69ee78d4a58c")
            if (result is not None):
                print(int.from_bytes(result))
            else:
                print("Failed to read")
        await client.disconnect()
    if device in connections:
        connections.remove(device)
    print("coolio we done here")


async def main():
    await scanner.start()


scanner = BleakScanner(Callback, ["2db9dd7d-1637-47db-96d4-495484ed45e7"])
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
