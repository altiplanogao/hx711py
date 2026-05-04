# AGENTS.md

Python library for HX711 24-bit ADC on Raspberry Pi.

## Library Versions
Two versions with different APIs:
- **Legacy** `hx711.py` (v0.1): snake_case API, install with `pip install -e .`
- **Preferred** `hx711v0_5_1.py` (v0.5.1): camelCase API, no install needed on Raspbian

Key API differences:
| Operation | Legacy (hx711.py) | New (hx711v0_5_1.py) |
|-----------|-------------------|----------------------|
| Set gain | `set_gain(128)` | `setGain(128)` |
| Set format | `set_reading_format()` | `setReadingFormat()` |
| Tare/offset | `tare()` | `autosetOffset()` |
| Read weight | `get_weight(times)` | `getWeight()` or callback |
| Set reference | `set_reference_unit()` | `setReferenceUnit()` |

New version supports interrupt-based (`--interrupt-based`, default) and polling-based (`--polling-based`) modes via `enableReadyCallback()`.

## Dependencies
`RPi.GPIO`, `rpi-lgpio` — **note:** `pyproject.toml` dependencies section has correct package names

## Key Commands
- New version (interrupt-based): `python example_hx711v0_5_1.py`
- New version (polling-based): `python example_hx711v0_5_1.py --polling-based`
- Listenable example: `python example_hx711_listenable.py`
- Emulator (no hardware): `python example_emulator.py`
- Legacy: `pip install -e . && python example.py`

## Hardware Quirks
- GPIO polling is time-sensitive on Linux: task scheduling causes random readings. For production, use MCU + I2C/1-Wire to Pi.
- Inconsistent readings? Adjust byte/bit order via `setReadingFormat("MSB", "MSB")` — first param is byte order, second is bit order (datasheet says MSB for bits).
- New version `readRawBytes(blockUntilReady=False)` returns `None` if lock is held (non-blocking for interrupt handler).

## Testing
No tests, CI, linting, or typechecking configured.

## Calibration
1. `hx.setReferenceUnit(1)` + `hx.autosetOffset()` (new) or `hx.tare()` (legacy)
2. Load 1kg weight, record `hx.getLong()` or `hx.read_long()`
3. `reference_unit = raw_long / 1000` (result in grams)
