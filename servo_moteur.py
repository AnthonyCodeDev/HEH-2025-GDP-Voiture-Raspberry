#!/usr/bin/env python3
import PCA9685 as PCA
import time

class ServoController:
    """
    Contrôleur de servo.

    Permet de positionner le servo via un angle relatif par rapport à la position centrale (0° relatif, correspondant généralement à 90° absolu).
    La plage de déplacement relative est ici étendue de -50° à +50°.

    Auteur : Anthony Vergeylen
    Date   : 08-04-2025
    """
    def __init__(self, center=320, minimum=200, maximum=500):
        self.pwm = PCA.PWM()
        self.pwm.frequency = 60
        self.center_val = center   # Valeur PWM correspondant à la position centrale (0° relatif)
        self.min_val = minimum     # Valeur PWM correspondant à -50°
        self.max_val = maximum     # Valeur PWM correspondant à +50°

    def rotate(self, angle):
        """
        Positionne le servo à un angle relatif compris entre -50° et +50°.
        Un angle positif déplace le servo vers la droite,
        un angle négatif vers la gauche.
        
        :param angle: Angle relatif désiré (entre -50 et 50).
        """
        # Contraindre l'angle dans l'intervalle [-50, 50]
        angle = max(-50, min(50, angle))
        if angle >= 0:
            pulse = self.center_val + ((angle / 50.0) * (self.max_val - self.center_val))
        else:
            pulse = self.center_val + ((angle / 50.0) * (self.center_val - self.min_val))
        self.pwm.write(0, 0, int(pulse))

    def disable_pwm(self):
        """
        Désactive la sortie PWM afin de ne pas maintenir le signal.
        Cela coupe le signal sur le canal PWM et permet au servo de ne plus être "maintenu".
        """
        self.pwm.write(0, 0, 4096)

def main():
    """
    Séquence de mouvement du servo :
      1. Remise en position centrale (0° relatif).
      2. Rotation à 50° vers la droite.
      3. Rotation à -50° (50° vers la gauche).
      4. Remise finale au centre.

    Après chaque commande, la sortie PWM est désactivée pour ne pas bloquer le signal.
    
    Auteur : Anthony Vergeylen
    Date   : 08-04-2025
    """
    servo = ServoController()
    
    # Position centrale
    servo.rotate(320)
    servo.disable_pwm()

if __name__ == "__main__":
    main()
