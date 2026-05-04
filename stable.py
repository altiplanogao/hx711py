from dataclasses import dataclass, field
import time
from collections import deque

@dataclass(frozen=True)
class StableInfo:
    count: int = 0
    value: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def __str__(self) -> str:
        ts = time.strftime('%H:%M:%S', time.localtime(self.timestamp))
        return f"[#{self.count} {self.value:.2f} {ts}]"

class StableChecker:
    def __init__(self, tolerance: float, fit_time_required: int = 5):
        self.tolerance = tolerance
        self.fit_time_required = fit_time_required
        self.window = deque(maxlen=fit_time_required)
        self.__stable_start = None
        self.__stable_duration = 0

    def check(self, value: float) -> bool:
        self.window.append(value)
        if len(self.window) < self.fit_time_required:
            return False
        stable = max(self.window) - min(self.window) <= self.tolerance
        if stable:
            if self.__stable_start is None:
                self.__stable_start = time.time()
            else:
                self.__stable_duration = time.time() - self.__stable_start
        else:
            self.__stable_start = None
            self.__stable_duration = 0
        return stable

    def get_stable_duration(self) -> float:
        return self.__stable_duration
