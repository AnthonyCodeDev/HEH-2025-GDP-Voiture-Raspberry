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
        # Désactive la sortie PWM dès l'initialisation pour éviter les impulsions intempestives
        self.disable_output()
        time.sleep(0.1)
        # Positionne le servo en position neutre
        self.reset()
        print("Servo initialisé. Position neutre définie.")

    def disable_output(self):
        """
        Désactive la sortie PWM sur le canal utilisé.
        En supposant que l'envoi de "off" = 4096 désactive la sortie.
        """
        self._servo.write(0, 0, 4096)

    def move(self, angle):
        """
        Positionne le servo à un angle compris entre -45° et 45°.
        """
        angle = max(-45, min(45, angle))
        if angle >= 0:
            pulse = self._center + ((angle / 45.0) * (self._max - self._center))
        else:
            pulse = self._center + ((angle / 45.0) * (self._center - self._min))
        self._servo.write(0, 0, int(pulse))

    def reset(self):
        """
        Positionne le servo à la valeur centrale (neutre).
        """
        self._servo.write(0, 0, int(self._center))

if __name__ == "__main__":
    servo = ServoController()
    # Optionnel : tester quelques mouvements après initialisation
    # time.sleep(1)
    # servo.move(45)
    # time.sleep(1)
    # servo.move(-45)
    # time.sleep(1)
    # servo.reset()
