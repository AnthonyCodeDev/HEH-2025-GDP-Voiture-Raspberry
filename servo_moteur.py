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
        self.pwm = PCA.PWM()
        self.pwm.frequency = 60
        self.center_val = center
        self.min_val = minimum
        self.max_val = maximum

    def rotate(self, angle):
        """
        Positionne le servo à un angle compris entre -45° et 45°.
        """
        angle = max(-45, min(45, angle))
        if angle > 0:
            pulse = self.center_val + ((angle / 45.0) * (self.max_val - self.center_val))
        else:
            pulse = self.center_val + ((angle / 45.0) * (self.center_val - self.min_val))
        self.pwm.write(0, 0, int(pulse))

    def disable_pwm(self):
        """
        Désactive la sortie PWM pour ne pas maintenir le signal.
        """
        self.pwm.write(0, 0, 4096)

def main():
    """
    Positionne le servo à 5° puis désactive la sortie PWM.
    
    Auteur : Anthony Vergeylen
    Date   : 08-04-2025
    """
    servo = ServoController()
    servo.rotate(5)
    time.sleep(1)  # Attendre que le servo atteigne la position
    servo.disable_pwm()

if __name__ == "__main__":
    main()
