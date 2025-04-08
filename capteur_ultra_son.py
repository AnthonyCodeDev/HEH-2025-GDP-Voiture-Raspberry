from gpiozero import DistanceSensor
from gpiozero.pins.pigpio import PiGPIOFactory
import time

# Capteur CD2 - GPIO 6 (TRIG), GPIO 5 (ECHO)
factory = PiGPIOFactory()
sensor_cd1 = DistanceSensor(echo=9, trigger=11, pin_factory=factory)
sensor_cd2 = DistanceSensor(echo=5, trigger=6, pin_factory=factory)
sensor_cd3 = DistanceSensor(echo=19, trigger=26, pin_factory=factory)

while True:
    try:
        print(f"[CD2] Distance1 : {sensor_cd1.distance * 100:.2f} cm")
        print(f"[CD2] Distance2 : {sensor_cd2.distance * 100:.2f} cm")
        print(f"[CD2] Distance3 : {sensor_cd3.distance * 100:.2f} cm")
        time.sleep(1)
    except Exception as e:
        print("❌ CD2 erreur :", e)
