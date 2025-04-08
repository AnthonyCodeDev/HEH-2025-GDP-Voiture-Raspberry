from gpiozero import DistanceSensor
from gpiozero.pins.pigpio import PiGPIOFactory
import time

factory = PiGPIOFactory()
sensor = DistanceSensor(echo=9, trigger=11, pin_factory=factory)

while True:
    print(f"Distance : {sensor.distance * 100:.2f} cm")
    time.sleep(1)
