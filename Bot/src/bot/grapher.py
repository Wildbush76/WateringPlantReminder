import logging
import os
import tempfile
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aiofiles
import matplotlib.pyplot as plt

_logger = logging.getLogger(__name__)


@asynccontextmanager
async def create_graph(
    data_file: str,
) -> AsyncGenerator[tempfile._TemporaryFileWrapper]:
    _logger.info("Creating graph")
    if not os.path.isfile(data_file):
        _logger.warning("Data file does not exist. Cannot make a graph")
        yield None
    else:
        try:
            timestamps = [1]
            values = [1]
            async with aiofiles.open(data_file, mode="r") as file:
                line = await file.readline()
                while line:
                    time, value = line.split(",")
                    timestamps.append(float(time))
                    values.append(int(value))
                    line = await file.readline()

            plt.plot(timestamps, values, color="blue")
            plt.grid(True)
            plt.title("Plant Soil Moisture")

            with tempfile.TemporaryFile() as file:
                plt.savefig(file, format="png", bbox_inches="tight")
                yield file

        except Exception:
            _logger.exception("Failed to create graph")
