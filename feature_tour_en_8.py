#!/usr/bin/env python3
import time, math
import RPi.GPIO as GPIO
from moteur import MotorController
from servo_controller import ServoController

class TourEn8:
    def __init__(self, speed=35, total_time=12, dt=0.02):
        self.motor = MotorController()
        self.servo = ServoController()
        self.speed = speed
        self.total_time = total_time
        self.dt = dt

    def run(self):
        start_time = time.time()
        try:
            while time.time() - start_time < self.total_time - 2:
                t = time.time() - start_time
                angle = 50 * math.sin(2 * math.pi * t / self.total_time)
                self.servo.rotate(angle)
                self.motor.forward(self.speed)
                time.sleep(self.dt)
            self.motor.stop()
            self.servo.resetRoue()
        finally:
            GPIO.cleanup()

if __name__ == "__main__":
    TourEn8().run()
