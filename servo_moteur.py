#!/usr/bin/env python3
import PCA9685 as PCA
import time

class ServoController:
    def __init__(self, center=320, minimum=200, maximum=500):
        self.servo = PCA.PWM()
        self.servo.frequency = 60
        self.center_val = center
        self.min_val = minimum
        self.max_val = maximum

    def rotate(self, angle):
        angle = max(-45, min(45, angle))
        if angle > 0:
            pulse = self.center_val + ((angle / 45.0) * (self.max_val - self.center_val))
        else:
            pulse = self.center_val + ((angle / 45.0) * (self.center_val - self.min_val))
        self.servo.write(0, 0, int(pulse))

    def reset_position(self):
        self.rotate(0)

if __name__ == "__main__":
    servo = SimpleServo()
    servo.reset_position()
    time.sleep(1)
    servo.rotate(45)
    time.sleep(1)
    servo.rotate(-45)
    time.sleep(1)
    servo.reset_position()
