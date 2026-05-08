from enum import Enum
from abc import ABC, abstractmethod
import asyncio


class WateringThresholds(Enum):
    HYDRATED = 0.6  # 1-0.6 is hydrated
    LITTLETHRISTY = 0.4
    THRISTY = 0.2
    DYING = 0


class PlantState(ABC):
    @abstractmethod
    def _voice_line(self) -> str:
        pass

    def __init__(self, message_callback):
        self._message_callback = message_callback
        message_callback(self._voice_line())

    async def RecieveMeasurement(self, measurement: float, delta: float):
        if delta > 0.03 and not isinstance(self, FreshyHydrated):
            if isinstance(self, MorePlease):
                return await self._RecieveMeasurement(measurement, delta)
            else:
                return MorePlease(self._message_callback)

        if measurement >= WateringThresholds.HYDRATED.value and not isinstance(self, FreshyHydrated):
            return FreshyHydrated(self._message_callback)
        elif measurement >= WateringThresholds.LITTLETHRISTY.value and not isinstance(self, ALittleThirsty):
            return ALittleThirsty(self._message_callback)
        elif measurement >= WateringThresholds.THRISTY.value and not isinstance(self, FarilyThirsty):
            return FarilyThirsty(self._message_callback)
        elif measurement >= WateringThresholds.DYING.value and not isinstance(self, DyingOfThirst):
            return DyingOfThirst(self._message_callback)
        else:
            return await self._RecieveMeasurement(measurement, delta)

    @abstractmethod
    async def _RecieveMeasurement(self, measurement: float, delta: float):
        return self


class MorePlease(PlantState):
    def _voice_line(self):
        return "morePlease"

    async def _RecieveMeasurement(self, measurement, delta):
        return self  # dont need any special logic


class ALittleThirsty(PlantState):
    def _voice_line(self):
        return "ALittleThirsty"

    async def _RecieveMeasurement(self, measurement, delta):
        return self  # dont need any special logic


class FarilyThirsty(PlantState):
    def _voice_line(self):
        return "Thirsty"

    async def _RecieveMeasurement(self, measurement, delta):
        return self  # dont need any special logic


class DyingOfThirst(PlantState):
    def _voice_line(self):
        return "Dying"

    def __init__(self, message_callback):
        super().__init__(message_callback)
        self.counter = 0

    async def _RecieveMeasurement(self, measurement, delta):
        self.counter += 1
        if self.counter > 48:
            return Dead(self._message_callback)
        else:
            return self


class Dead(PlantState):
    def _voice_line(self):
        return "Dead"

    async def _RecieveMeasurement(self, measurement, delta):
        return self


class TooMuchWater(PlantState):
    def _voice_line(self):
        return "TooMuch"

    async def _RecieveMeasurement(self, measurement, delta):
        return self


class FreshyHydrated(PlantState):
    def __init__(self, message_callback):
        super().__init__(message_callback)
        self.counter = 0

    def _voice_line(self):
        return "freshyHydrated"

    async def _RecieveMeasurement(self, measurement: float, delta: float):
        self.counter += 1
        if (self.counter > 24 * 5):
            return TooMuchWater(self._message_callback)
        return self
