from enum import Enum
from abc import ABC, abstractmethod
import asyncio


class WateringThresholds(Enum):
    HYDRATED = 0.6  # 1-0.6 is hydrated
    LITTLETHRISTY = 0.4
    THRISTY = 0.2
    DYING = 0
    WATERED = 0.33  # min delta for the plant to have gotten water


class PlantState(ABC):
    @abstractmethod
    def _voice_line(self) -> str:
        pass

    def __init__(self, message_callback):
        self._message_callback = message_callback
        message_callback(self._voice_line())

    @abstractmethod
    async def RecieveMeasurement(self, measurement: float, delta: float):
        pass


class MorePlease(PlantState):
    def _voice_line(self):
        return "morePlease"

    async def RecieveMeasurement(self, measurement, delta):
        if measurement >= WateringThresholds.HYDRATED.value:
            return FreshyHydrated(self._message_callback)
        elif measurement >= WateringThresholds.LITTLETHRISTY.value:
            return ALittleThirsty(self._message_callback)
        elif measurement >= WateringThresholds.THRISTY.value:
            return Thirsty(self._message_callback)
        elif measurement >= WateringThresholds.DYING.value:
            return DyingOfThirst(self._message_callback)


class ALittleThirsty(PlantState):
    def _voice_line(self):
        return "ALittleThirsty"

    async def RecieveMeasurement(self, measurement, delta):
        if delta > WateringThresholds.WATERED.value:
            return MorePlease(self._message_callback)

        if measurement >= WateringThresholds.HYDRATED.value:
            return FreshyHydrated(self._message_callback)
        elif measurement <= WateringThresholds.DYING.valu:
            return DyingOfThirst(self._message_callback)
        elif measurement <= WateringThresholds.THRISTY.value:
            return Thirsty(self._message_callback)
        else:
            return self


class Thirsty(PlantState):
    def _voice_line(self):
        return "Thirsty"

    async def RecieveMeasurement(self, measurement, delta):
        if delta > WateringThresholds.WATERED.value:
            return MorePlease(self._message_callback)

        if measurement >= WateringThresholds.HYDRATED.value:
            return FreshyHydrated(self._message_callback)
        elif measurement <= WateringThresholds.THRISTY.value:
            return Dead(self._message_callback)
        else:
            return self


class DyingOfThirst(PlantState):
    def _voice_line(self):
        return "Dying"

    def __init__(self, message_callback):
        super().__init__(message_callback)
        self.counter = 0

    async def RecieveMeasurement(self, measurement, delta):
        if delta > WateringThresholds.WATERED.value:
            return MorePlease(self._message_callback)

        if measurement >= WateringThresholds.HYDRATED.value:
            return FreshyHydrated(self._message_callback)

        self.counter += 1
        if self.counter > 3:
            return Dead(self._message_callback)
        else:
            return self


class Dead(PlantState):
    def _voice_line(self):
        return "Dead"

    async def RecieveMeasurement(self, measurement, delta):
        if delta > WateringThresholds.WATERED.value:
            return MorePlease(self._message_callback)

        if measurement >= WateringThresholds.HYDRATED.value:
            return FreshyHydrated(self._message_callback)
        return self


class TooMuchWater(PlantState):
    def _voice_line(self):
        return "TooMuch"

    async def RecieveMeasurement(self, measurement, delta):
        if measurement >= WateringThresholds.HYDRATED.value:
            return self
        elif measurement >= WateringThresholds.LITTLETHRISTY.value:
            return ALittleThirsty(self._message_callback)
        elif measurement >= WateringThresholds.THRISTY.value:
            return Thirsty(self._message_callback)
        else:
            return DyingOfThirst(self._message_callback)


class FreshyHydrated(PlantState):
    def __init__(self, message_callback):
        super().__init__(message_callback)
        self.counter = 0

    def _voice_line(self):
        return "freshyHydrated"

    async def RecieveMeasurement(self, measurement: float, delta: float):
        self.counter += 1
        if (self.counter > 1 * 3):
            return TooMuchWater(self._message_callback)

        if measurement >= WateringThresholds.HYDRATED.value:
            return self
        elif measurement >= WateringThresholds.LITTLETHRISTY.value:
            return ALittleThirsty(self._message_callback)
        elif measurement >= WateringThresholds.THRISTY.value:
            return Thirsty(self._message_callback)
        elif measurement >= WateringThresholds.DYING.value:
            return DyingOfThirst(self._message_callback)
