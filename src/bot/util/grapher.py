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
        values: list[list[float | str]] = []
        async with aiofiles.open(data_file, mode="r") as file:
            headers = (await file.readline()).split(",")
            values = [[header] for header in headers]

            line = await file.readline()
            while line:
                for i, value in enumerate(line.split(",")):
                    values[i].append(float(value))
                line = await file.readline()

        if len(values) == 0:
            return None  # nothing to graph
        # edit the timestamps
        epoch = values[0][1]
        SECONDS_PER_DAY = (60) * (60) * (24)
        timestamps = [(t - epoch) / SECONDS_PER_DAY for t in values[0][1:]]

        for value in values[1:]:
            plt.plot(timestamps, value[1:], label=value[0])

        plt.grid(True)
        plt.title("Plant Soil Moisture")

        plt.xlabel("Time (Days)")
        plt.ylabel("Readings")
        plt.legend()
        image = io.BytesIO()

        plt.savefig(image, format="png", bbox_inches="tight")
        plt.close()
        image.seek(0)
        return image

    except Exception:
        _logger.exception("Failed to create graph")
