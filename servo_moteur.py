#!/usr/bin/env python3
import PCA9685 as PCA
import time

class ServoController:
    """
    Contrôleur de servo.
    
    Permet de positionner le servo via un angle relatif par rapport à la position centrale (0° relatif,
    correspondant généralement à 90° absolu). La plage de déplacement relative est ici étendue de -50° à +50°.
    
    Auteur : Anthony Vergeylen
    Date   : 08-04-2025
    """
    def __init__(self, center=320, minimum=200, maximum=500):
        self.pwm = PCA.PWM()
        self.pwm.frequency = 60
        self.center_val = center    # PWM pour la position centrale (0° relatif)
        self.min_val = minimum      # PWM pour -50° relatif
        self.max_val = maximum      # PWM pour +50° relatif

    def rotate(self, angle):
        """
        Positionne le servo à un angle relatif compris entre -50° et +50°.
        Un angle positif déplace le servo vers la droite, un angle négatif vers la gauche.
        
        :param angle: Angle relatif désiré (entre -50 et 50).
        """
        # Contrainte de l'angle dans l'intervalle [-50, 50]
        original_angle = angle
        angle = max(-50, min(50, angle))
        if angle >= 0:
            pulse = self.center_val + ((angle / 50.0) * (self.max_val - self.center_val))
        else:
            pulse = self.center_val + ((angle / 50.0) * (self.center_val - self.min_val))
        print(f"rotate({original_angle}) => Angle contraint: {angle} -> Pulse: {int(pulse)}")
        self.pwm.write(0, 0, int(pulse))

    def disable_pwm(self):
        """
        Désactive la sortie PWM afin de ne pas maintenir le signal.
        Cela coupe le signal sur le canal PWM pour libérer le servo.
        """
        print("Désactivation du PWM (envoi de 4096).")
        self.pwm.write(0, 0, 4096)

def main():
    """
    Séquence de mouvement du servo :
      1. Positionnement à 0° relatif (centre) puis attente 5 secondes.
      2. Rotation vers la droite à +50° relatif puis attente 5 secondes.
      3. Rotation vers la gauche à -50° relatif puis attente 5 secondes.
      4. Remise au centre (0° relatif) puis désactivation du PWM.
    
    Après chaque commande, la sortie PWM est désactivée pour libérer le servo.
    
    Auteur : Anthony Vergeylen
    Date   : 08-04-2025
    """
    servo = ServoController()
    
    # 1. Positionnement au centre (0° relatif)
    print("Positionnement au centre (0° relatif)")
    servo.rotate(0)
    servo.disable_pwm()
    time.sleep(5)
    
    # 2. Rotation vers la droite (+50° relatif)
    print("Rotation vers la droite (+50° relatif)")
    servo.rotate(50)
    servo.disable_pwm()
    time.sleep(5)
    
    # 3. Rotation vers la gauche (-50° relatif)
    print("Rotation vers la gauche (-50° relatif)")
    servo.rotate(-50)
    servo.disable_pwm()
    time.sleep(5)
    
    # 4. Remise au centre et désactivation du PWM
    print("Remise au centre (0° relatif) et désactivation finale du PWM")
    servo.rotate(0)
    servo.disable_pwm()

if __name__ == "__main__":
    main()
