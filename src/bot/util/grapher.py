import io
import logging
import os

import aiofiles
import matplotlib.pyplot as plt

_logger = logging.getLogger(__name__)


async def create_graph(data_file: str) -> io.BytesIO | None:
    _logger.info("Creating graph")
    if not os.path.isfile(data_file):
        _logger.warning("Data file does not exist. Cannot make a graph")
        return

    try:
        timestamps = []
        values = []
        async with aiofiles.open(data_file, mode="r") as file:
            line = await file.readline()
            while line:
                time, value = line.split(",")
                timestamps.append(float(time))
                values.append(int(value))
                line = await file.readline()

        if len(timestamps) == 0:
            return None  # nothing to graph
        # edit the timestamps
        epoch = timestamps[0]
        SECONDS_PER_DAY = (60) * (60) * (24)
        timestamps = [(t - epoch) / SECONDS_PER_DAY for t in timestamps]

        plt.plot(timestamps, values, color="blue")
        plt.grid(True)
        plt.title("Plant Soil Moisture")
        plt.xlabel("Time (Days)")
        plt.ylabel("Readings")
        image = io.BytesIO()

        plt.savefig(image, format="png", bbox_inches="tight")
        image.seek(0)
        return image

    except Exception:
        _logger.exception("Failed to create graph")
