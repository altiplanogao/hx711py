from typing import Optional, Callable
import time
import threading
from hx711v0_5_1 import HX711
from stable import StableInfo, StableChecker
from average_calc import ExponentialMovingAverageCalculator

class HX711Listenable(HX711):
    STABLE_REQUIRED_SECONDS = 1.0
    TOLERANCE_GRAMS = 5
    tolerance = 13

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__check_period_second = 0.2
        self.__last_long_value = 0
        self.__enable_interrupt_caching()
        self.__interrupt_index = 0
        # Weight change detection
        self.__stable_average_calculator = ExponentialMovingAverageCalculator(alpha=0.3)
        self.__last_stable_info: Optional[StableInfo] = None
        self.__callback: Optional[Callable[[StableInfo], None]] = None
        self.__weight_check_stop_event = threading.Event()
        self.__weight_listen_thread = None

    def set_weight_change_callback(self, callback: Optional[Callable[[StableInfo], None]]) -> None:
        self.__callback = callback

    def start_weight_checking(self):
        if self.__weight_listen_thread is not None and self.__weight_listen_thread.is_alive():
            return
        self.__weight_check_stop_event.clear()
        self.__weight_listen_thread = threading.Thread(target=self.__weight_periodic_checker, daemon=True)
        self.__weight_listen_thread.start()

    def stop_weight_checking(self):
        self.__weight_check_stop_event.set()

    def __weight_periodic_checker(self):
        stable_checker = StableChecker(tolerance=self.TOLERANCE_GRAMS,
                                    fit_time_required=int(self.STABLE_REQUIRED_SECONDS / self.__check_period_second))
        weight_index = 0
        while not self.__weight_check_stop_event.is_set():
            weight_index += 1
            current_weight = self.get_weight_from_raw_value(self.__last_long_value)
            self.__stable_average_calculator.push(current_weight)
            current_average_weight = self.__stable_average_calculator.get()
            is_stable = stable_checker.check(current_average_weight)
            last_stable = self.__last_stable_info if self.__last_stable_info is not None else StableInfo()
            print(f"[W #{weight_index}]. last stable: {last_stable}, current:{current_average_weight:.1f} grams, stable: {is_stable}")
            if is_stable:
                last_stable_weight = last_stable.value
                diff_than_last_stable = abs(current_average_weight - last_stable_weight)
                if diff_than_last_stable > self.TOLERANCE_GRAMS:
                    if stable_checker.get_stable_duration() > self.STABLE_REQUIRED_SECONDS:
                        pre_stable = last_stable
                        current_stable = StableInfo(
                            count=pre_stable.count+1,
                            value=current_average_weight,
                        )
                        update_delay = current_stable.timestamp - pre_stable.timestamp
                        self.__last_stable_info = current_stable
                        if self.__callback:
                            self.__callback(current_stable)
                        print(f"[W-NEW-STABLE] #{weight_index}. {pre_stable:} -> {current_stable} grams after {update_delay:.1f} seconds")
            time.sleep(self.__check_period_second)

    def __enable_interrupt_caching(self):
        def update_cache(rawBytes):
            long_value = self.rawBytesToLong(rawBytes)
            if long_value == -1:
                return
            self.__interrupt_index += 1
            self.__last_long_value = long_value
        self.enableReadyCallback(update_cache)

    def autosetOffset(self):
        check_times = int(self.STABLE_REQUIRED_SECONDS / self.__check_period_second)
        average = ExponentialMovingAverageCalculator(alpha=0.2)
        average_value = 0
        equal_times = 0
        loops = 0
        start_time = time.time() 
        while True:
            loops += 1
            average.push(self.__last_long_value)
            current_average_value = average.get()
            value_diff = average_value - current_average_value
            elapsed = time.time() - start_time
            if abs(value_diff) < self.tolerance:
                equal_times += 1
                if equal_times >= check_times:
                    print(f"[AUTO SET OFFSET] offset: #{loops}. {average_value} (stable for {equal_times} times) Elapsed: {elapsed:.1f}s")
                    self.setOffset(average_value)
                    break
                print(f"[AUTO SET OFFSET] offset: #{loops}. {average_value} ({equal_times} times) Elapsed: {elapsed:.1f}s")
            else:
                equal_times = 0
                average_value = current_average_value
                print(f"[AUTO SET OFFSET] offset: #{loops}. {average_value} Elapsed: {elapsed:.1f}s")
            time.sleep(self.__check_period_second)
        self.__last_stable_info = StableInfo(count=0, value=0.0)

    def get_last_long_value(self):
        return self.__last_long_value

    def get_weight_from_raw_value(self, raw):
        if raw == None:
            return 0
        return (raw - self.getOffset()) / self.getReferenceUnit()
