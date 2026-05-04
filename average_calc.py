from abc import ABC, abstractmethod
from collections import deque

class AverageCalculator(ABC):
    @abstractmethod
    def push(self, val: float) -> None:
        pass

    @abstractmethod
    def get(self) -> float:
        pass

class SimpleMovingAverageCalculator(AverageCalculator):
    def __init__(self, window_size: int = 10):
        # deque with maxlen automatically removes oldest elements when full
        self.window = deque(maxlen=window_size)

    def push(self, val: float) -> None:
        self.window.append(val)  # Automatically manages size, no overflow

    def get(self) -> float:
        if not self.window:
            return 0.0
        return sum(self.window) / len(self.window)

class ExponentialMovingAverageCalculator(AverageCalculator):
    def __init__(self, alpha: float = 0.1):
        self.alpha = alpha
        self.ema = None

    def push(self, val: float) -> None:
        if self.ema is None:
            self.ema = val
        else:
            self.ema = self.alpha * val + (1 - self.alpha) * self.ema

    def get(self) -> float:
        return self.ema if self.ema is not None else 0.0
