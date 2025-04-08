#!/usr/bin/env python3
import PCA9685 as PCA
import time

class ServoController:
    """
    Contrôleur de servo pour les roues.
    
    Permet de positionner les roues via un angle relatif par rapport à la position centrée (0° relatif),
    correspondant à des roues droites. La plage de déplacement relative est ici étendue de -50° à +50°.
    
    Auteur : Anthony Vergeylen
    Date   : 08-04-2025
    """
    def __init__(self, center=320, minimum=200, maximum=500):
        self.pwm = PCA.PWM()
        self.pwm.frequency = 60
        self.center_val = center   # Valeur PWM pour des roues droites (0° relatif)
        self.min_val = minimum     # Valeur PWM pour -50° relatif
        self.max_val = maximum     # Valeur PWM pour +50° relatif

    def rotate(self, angle):
        """
        Positionne les roues à un angle relatif compris entre -50° et +50°.
        Un angle positif déplace les roues vers la droite, un angle négatif vers la gauche.
        
        :param angle: Angle relatif désiré (entre -50 et 50).
        """
        # Contraindre l'angle dans [-50, 50]
        angle = max(-50, min(50, angle))
        if angle >= 0:
            pulse = self.center_val + ((angle / 50.0) * (self.max_val - self.center_val))
        else:
            pulse = self.center_val + ((angle / 50.0) * (self.center_val - self.min_val))
        self.pwm.write(0, 0, int(pulse))
        print(f"rotate({angle}) -> PWM: {int(pulse)}")

    # def settodegree (pas juste rotate, mais mettre à une position précise)
    def setToDegree(self, angle):
        """
        Positionne les roues à un angle absolu entre 0° et 180°.
        Un angle de 0° correspond à la position centrée (0° relatif).
        
        :param angle: Angle absolu désiré (entre 0 et 180).
        """
        # Contraindre l'angle dans [0, 180]
        angle = max(0, min(180, angle))
        pulse = self.center_val + ((angle / 180.0) * (self.max_val - self.min_val))
        self.pwm.write(0, 0, int(pulse))
        print(f"setToDegree({angle}) -> PWM: {int(pulse)}")

    def resetRoue(self):
        """
        Remet les roues en position droite (0° relatif).
        Force la valeur PWM à la valeur centrée calibrée, 
        garantissant ainsi que les roues sont bien droites.
        """
        self.pwm.write(0, 0, int(self.center_val))
        print(f"resetRoue() -> PWM: {int(self.center_val)}")

    def disable_pwm(self):
        """
        Désactive la sortie PWM pour libérer le servo (les roues ne maintiennent plus une position active).
        """
        self.pwm.write(0, 0, 4096)
        print("PWM désactivé.")

def main():
    """
    Test du réajustement des roues :
      1. On positionne les roues à +50°.
      2. On attend 5 secondes.
      3. On réinitialise les roues à 0° relatif (droites) à l'aide de resetRoue().
      4. On désactive le signal PWM.
    """
    servo = ServoController()
    
    print("Rotation des roues à +50°...")
    servo.setToDegree(45)
    time.sleep(5)
    
    servo.disable_pwm()

if __name__ == "__main__":
    main()
