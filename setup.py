from setuptools import setup

setup(
    name='hx711',
    version='0.1.0',
    description='HX711 Python Library for Raspberry Pi',
    py_modules=['hx711', 'hx711v0_5_1'],
    install_requires=['Rpi.GPIO', 'rpi-lgpio'],
)

