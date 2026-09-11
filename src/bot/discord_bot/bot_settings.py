from pathlib import Path

from pydantic_settings import BaseSettings


class PlantSettings(BaseSettings):
    data_path: str = "/var/lib/plant_bot/"
    log_file_name: str = "logs.txt"
    data_file_name: str = "data.csv"
    characteristicUUID: str = "38072c05-608d-441e-987e-69ee78d4a58c"
    serviceUUID: str = "2db9dd7d-1637-47db-96d4-495484ed45e7"
    voice_line_folder: str = "VoiceLines"
    target_user: int = 704773768035172726
    owner: int = 704773768035172726

    @property
    def data_file(self) -> Path:
        return Path(self.data_path, self.data_file_name).absolute()

    @property
    def log_file(self) -> Path:
        return Path(self.data_path, self.log_file_name)
