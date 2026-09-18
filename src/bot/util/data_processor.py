import time
from collections import deque
from pathlib import Path

import aiofiles


class DataProcessor:
    WINDOW_SiZE = 10

    def __init__(self, data_file: Path):
        self._data_file = data_file

        self._load_averaging_window()

    def _load_averaging_window(self):
        self._window = deque()
        if not self._data_file.is_file():
            for _ in range(self.WINDOW_SiZE):
                self._window.append(0)
            return

        with open(self._data_file, "r") as file:
            data = file.read().split("\n")[-self.WINDOW_SiZE : 0]
            for d in data:
                self._window.append(d[1])

    async def _get_windowed_average(self, value: int) -> float:
        self._window.append(value)
        self._window.popleft()

        average = sum(self._window) / len(self._window)
        return average

    async def process_reading(self, value: int) -> None:
        self._last_read_time = time.time()
        averaged = self._get_windowed_average(value)

        await self._log_reading(value, averaged)

    async def _log_reading(self, reading: int, averaged: float) -> None:
        new_file = not self._data_file.is_file()

        async with aiofiles.open(self._data_file, mode="a") as file:
            if new_file:
                await file.write("Timestamp,Raw_Values,Averaged")  # Headers
            await file.write(f"{time.time()},{reading},{averaged}\n")
