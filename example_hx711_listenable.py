from typing import Optional, Callable
import time
import sys
import threading
import RPi.GPIO as GPIO

from average_calc import ExponentialMovingAverageCalculator
from hx711_listenable import HX711Listenable

if __name__ == "__main__":
    hx = HX711Listenable(dout=15, pd_sck=14, gain=64)
    hx.setReadingFormat("MSB", "MSB")

    print("[INFO] Automatically setting the offset.")
    hx.autosetOffset()
    offsetValue = hx.getOffset()
    print(f"[INFO] Finished automatically setting the offset. The new value is '{offsetValue}'.")

    referenceUnit = 13.71
    hx.setReferenceUnit(referenceUnit)

    # hx.set_weight_change_callback(lambda stable_info: print(f"[CALLBACK] Detected stable weight change! {stable_info}"))
    hx.start_weight_checking()

    # Average calculator for sliding window average
    avg_calculator = ExponentialMovingAverageCalculator()
    while True:
        try:
            # getRawBytesAndPrintAll()
            # Interrupt-based mode: read from cache at 5Hz and compute sliding average
            time.sleep(0.2)  # 5Hz = 1/0.2 seconds
            # latest_long = hx.get_last_long_value()
            # if latest_long is not None:
            #     avg_calculator.push(hx.get_weight_from_raw_value(latest_long))
            #     avg_weight = avg_calculator.get()
            #     print(f"[SLIDING AVERAGE] Average weight: {avg_weight:.2f} gr. last_long: {latest_long}")
            #     # print(f"[SLIDING AVERAGE] Average weight: {avg_weight:.2f} gr")
                
        except (KeyboardInterrupt, SystemExit):
            GPIO.cleanup()
            print("[INFO] 'KeyboardInterrupt Exception' detected. Cleaning and exiting...")
            sys.exit()
        