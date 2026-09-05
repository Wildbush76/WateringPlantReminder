from pydantic import BaseModel


class PlantConfigs(BaseModel):
    filename: str
    characteristicUUID: str
    serviceUUID: str
    voiceFolder: str
    vicitim: int
