from pydantic_settings import BaseSettings


class PlantSettings(BaseSettings):
    discord_token: str
    data_file: str = "data.csv"
    characteristicUUID: str = "38072c05-608d-441e-987e-69ee78d4a58c"
    serviceUUID: str = "2db9dd7d-1637-47db-96d4-495484ed45e7"
    voice_line_folder: str = "VoiceLines"
    target_user: int = 704773768035172726
