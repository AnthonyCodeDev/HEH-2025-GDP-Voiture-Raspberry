#!/usr/bin/env python3
import time, math
import RPi.GPIO as GPIO
from moteur import MotorController
from servo_controller import ServoController

class TourEn8:
    def __init__(self, speed=35, cycle_time=12, dt=0.03, cycles=3, amplitude=90):
        self.motor = MotorController()
        self.servo = ServoController()
        self.speed = speed
        self.cycle_time = cycle_time
        self.dt = dt
        self.cycles = cycles
        self.amplitude = amplitude

    def run(self):
        try:
            for _ in range(self.cycles):
                start = time.time()
                while time.time() - start < self.cycle_time:
                    t = time.time() - start
                    angle = 45 + self.amplitude * math.sin(2 * math.pi * t / self.cycle_time)
                    self.servo.setToDegree(angle)
                    self.motor.forward(self.speed)
                    time.sleep(self.dt)
                self.motor.stop()
                self.servo.setToDegree(45)
                time.sleep(1)
        finally:
            self.motor.stop()
            self.servo.disable_pwm()
            GPIO.cleanup()

if __name__ == "__main__":
    TourEn8().run()
