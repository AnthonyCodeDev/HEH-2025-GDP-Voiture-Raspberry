#!/usr/bin/env python3
import PCA9685 as PCA
import time

class ServoController:
    """
    Contrôleur de servo.

    Auteur : Anthony Vergeylen
    Date   : 08-04-2025
    """
    def __init__(self, center=320, minimum=200, maximum=500):
        self._servo = PCA.PWM()
        self._servo.frequency = 60
        self._center = center
        self._min = minimum
        self._max = maximum

    def move(self, angle):
        """
        Positionne le servo à un angle compris entre -45° et 45°.

        :param angle: Angle souhaité en degrés.
        """
        angle = max(-45, min(45, angle))
        if angle >= 0:
            pulse = self._center + ((angle / 45.0) * (self._max - self._center))
        else:
            pulse = self._center + ((angle / 45.0) * (self._center - self._min))
        self._servo.write(0, 0, int(pulse))

    def reset(self):
        """
        Positionne le servo à la valeur centrale pour éviter tout mouvement intempestif.
        """
        self._servo.write(0, 0, int(self._center))

if __name__ == "__main__":
    servo = ServoController()
    servo.reset()
    # Optionnel pour tester le mouvement :
    # time.sleep(1)
    # servo.move(45)
    # time.sleep(1)
    # servo.move(-45)
    # time.sleep(1)
    # servo.reset()
