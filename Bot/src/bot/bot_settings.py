from pydantic_settings import BaseSettings


class PlantSettings(BaseSettings):
    discord_token: str
    command_prefix: str = "!"
    data_file: str = "data.csv"
    characteristicUUID: str
    serviceUUID: str
    voice_line_folder: str = "VoiceLines"
    target_user: int
