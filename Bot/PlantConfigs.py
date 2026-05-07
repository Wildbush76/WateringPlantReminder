import json
import os


class PlantConfigs:
    def __init__(self, filename: str):
        self._filename = filename
        self.characteristicUUID = None
        self.serviceUUID = None
        self.voiceFolder = None
        self.vicitim = None
        self._loadConfigs(filename)

    def _saveConfigs(self) -> None:
        configs = {}
        for attribute in dir(self):
            if not attribute.startswith("_"):
                configs[attribute] = self.__getattribute__(attribute)
        with open(self._filename, "w") as file:
            json.dump(configs, file)

    def _loadConfigs(self, filename: str) -> None:
        configs = {}
        if os.path.isfile(filename):
            with open(filename, "r") as file:
                configs = json.load(file)
        else:
            self._saveConfigs()
            return
        for key in configs:
            self.__setattr__(key, configs[key])
