#!/usr/bin/env python3
import PCA9685 as PCA
import time

class ServoController:
    """
    Contrôleur de servo.
    
    Permet de positionner le servo avec un angle relatif par rapport à la position neutre (90° absolu).
    La plage de déplacement relative est de -45° à +45°.
    
    Auteur : Anthony Vergeylen
    Date   : 08-04-2025
    """
    def __init__(self, center=320, minimum=200, maximum=500):
        self.pwm = PCA.PWM()
        self.pwm.frequency = 60
        self.center_val = center   # Valeur PWM correspondant à la position neutre (90° absolu)
        self.min_val = minimum     # Valeur PWM pour -45° relatif (extrémité gauche)
        self.max_val = maximum     # Valeur PWM pour +45° relatif (extrémité droite)

    def rotate(self, angle):
        """
        Positionne le servo à un angle relatif.
        
        L'angle passé en paramètre est relatif à la position neutre (0° = 90° absolu).
        Un angle positif déplace le servo vers la droite, un angle négatif vers la gauche.
        La valeur de l'angle est forcée dans la plage [-45, 45].
        
        :param angle: Angle relatif souhaité (entre -45 et 45).
        """
        # Contraindre l'angle dans l'intervalle [-45, 45]
        angle = max(-45, min(45, angle))
        if angle > 0:
            pulse = self.center_val + ((angle / 45.0) * (self.max_val - self.center_val))
        else:
            pulse = self.center_val + ((angle / 45.0) * (self.center_val - self.min_val))
        self.pwm.write(0, 0, int(pulse))

    def reset_position(self):
        """
        Remet le servo en position neutre (0° relatif, donc 90° absolu).
        """
        self.rotate(0)

    def disable_pwm(self):
        """
        Désactive la sortie PWM afin de ne pas maintenir le signal.
        Cette commande envoie une valeur qui coupe le signal sur le canal.
        """
        self.pwm.write(0, 0, 4096)

def main():
    """
    Exécute la séquence suivante :
      1. Tourner à droite de 10° relatif (donc position à +10°).
      2. Désactiver la sortie PWM pour libérer le servo (il ne maintient pas le signal).
      3. Attendre 4 secondes.
      4. Tourner à gauche de 10° relatif (donc position à -10°).
      5. Désactiver la sortie PWM et attendre 4 secondes.
      6. Remettre le servo en position neutre (0° relatif) et désactiver la sortie.
      
    Ainsi, la commande rotate(n) positionne le servo en absolu (n étant l'angle relatif souhaité).
    Par exemple, rotate(10) place le servo à +10° et rotate(-10) le place à -10°.
    """
    servo = ServoController()
    
    # Tourner vers la droite à +10° relatif
    servo.rotate(10)
    servo.disable_pwm()
    time.sleep(4)
    
    # Tourner vers la gauche à -10° relatif (donc positionner à -10° et non à revenir au 0°)
    servo.rotate(-10)
    servo.disable_pwm()
    time.sleep(4)
    
    # Remettre en position neutre (0° relatif)
    servo.reset_position()
    servo.disable_pwm()

if __name__ == "__main__":
    main()
