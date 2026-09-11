from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class PlantSettings(BaseSettings):
    data_path: str = "/var/lib/plant_bot/"
    _log_file: str = Field(validation_alias="log_file", default="logs.txt")
    _data_file: str = Field(validation_alias="data_file", default="data.csv")
    characteristicUUID: str = "38072c05-608d-441e-987e-69ee78d4a58c"
    serviceUUID: str = "2db9dd7d-1637-47db-96d4-495484ed45e7"
    voice_line_folder: str = "VoiceLines"
    target_user: int = 704773768035172726

    @property
    def data_file(self) -> str:
        return str(Path(self.data_path, self._data_file).absolute())

    @property
    def log_file(self) -> str:
        return str(Path(self.data_path, self._log_file).absolute())
