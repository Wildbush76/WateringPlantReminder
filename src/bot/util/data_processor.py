import time
from collections import deque
from pathlib import Path

import aiofiles

# TODO replace csv with a better datatype or just make this code cleaner


class DataProcessor:
    WINDOW_SiZE = 10

    def __init__(self, data_file: Path):
        self._data_file = data_file

        self._load_averaging_window()

    def _load_averaging_window(self):
        self._window = deque()
        if not self._data_file.exists():
            return

        with open(self._data_file, "r") as file:
            rows = file.read().strip().split("\n")[1:]

            v = min(self.WINDOW_SiZE, len(rows))

            data = rows[-v:]
            data = [d.split(",")[1] for d in data]

            for d in data:
                self._window.append(float(d))

    async def _get_windowed_average(self, value: int) -> float:
        self._window.append(value)
        if len(self._window) > self.WINDOW_SiZE:
            self._window.popleft()

        average = sum(self._window) / len(self._window)
        return average

    async def process_reading(self, value: int) -> None:
        self._last_read_time = time.time()
        averaged = await self._get_windowed_average(value)

        await self._log_reading(value, averaged)

    async def _log_reading(self, reading: int, averaged: float) -> None:
        new_file = not self._data_file.exists()

        async with aiofiles.open(self._data_file, mode="a") as file:
            if new_file:
                await file.write("Timestamp,Raw_Values,Averaged\n")  # Headers
            await file.write(f"{time.time()},{reading},{averaged}\n")
