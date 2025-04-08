#!/usr/bin/env python3
import PCA9685 as PCA
import time

class ServoController:
    def __init__(self, center=320, minimum=200, maximum=500):
        self._servo = PCA.PWM()
        self._servo.frequency = 60
        self._center = center
        self._min = minimum
        self._max = maximum
        self.disable_output()
        time.sleep(0.1)
        self.enable_output()
        self.reset()
        print("Servo initialisé. Position neutre définie.")

    def disable_output(self):
        self._servo.write(0, 0, 4096)

    def enable_output(self):
        # Écriture d'une valeur valide (<4096) permet de réactiver la sortie
        self._servo.write(0, 0, 0)

    def move(self, angle):
        angle = max(-45, min(45, angle))
        if angle >= 0:
            pulse = self._center + ((angle / 45.0) * (self._max - self._center))
        else:
            pulse = self._center + ((angle / 45.0) * (self._center - self._min))
        self._servo.write(0, 0, int(pulse))

    def reset(self):
        self._servo.write(0, 0, int(self._center))

if __name__ == "__main__":
    servo = ServoController()
