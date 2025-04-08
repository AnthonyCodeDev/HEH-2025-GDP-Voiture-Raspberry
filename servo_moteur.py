#!/usr/bin/env python3
import PCA9685 as PCA
import time

class ControleurServoRoue:
    """
    Contrôleur de servo pour la direction des roues.

    Permet de positionner les roues par un angle relatif par rapport à la position centrale (0° relatif,
    c'est-à-dire les roues droites). La plage de déplacement relative est ici étendue de -50° à +50°.

    Auteur : Anthony Vergeylen
    Date   : 08-04-2025
    """
    def __init__(self, pwm_centre=320, pwm_min=200, pwm_max=500):
        self.pwm = PCA.PWM()
        self.pwm.frequency = 60
        self.centre = pwm_centre   # Valeur PWM pour les roues droites (0° relatif)
        self.min = pwm_min         # Valeur PWM pour -50° relatif (roues tournées à gauche)
        self.max = pwm_max         # Valeur PWM pour +50° relatif (roues tournées à droite)

    def tourner_angle_relatif(self, angle):
        """
        Positionne les roues à un angle relatif compris entre -50° et +50°.
        Un angle positif fait tourner les roues vers la droite, un angle négatif vers la gauche.
        
        :param angle: Angle relatif souhaité (entre -50 et +50).
        """
        angle = max(-50, min(50, angle))  # Contraindre l'angle dans [-50, 50]
        if angle >= 0:
            impulsion = self.centre + ((angle / 50.0) * (self.max - self.centre))
        else:
            impulsion = self.centre + ((angle / 50.0) * (self.centre - self.min))
        self.pwm.write(0, 0, int(impulsion))
        print(f"tourner_angle_relatif({angle}) -> PWM: {int(impulsion)}")

    def setAngleAbsolu(self, angle):
        """
        Positionne les roues à un angle absolu entre 0° et 180°.
        Ici, 0° correspond à la position centrale (roues droites).
        
        :param angle: Angle absolu souhaité (entre 0 et 180).
        """
        angle = max(0, min(180, angle))
        # On mappe l'angle absolu à une impulsion PWM.
        # 0° correspond à la valeur 'centre' et 180° correspond à centre + (max - min)
        impulsion = self.centre + ((angle / 180.0) * (self.max - self.min))
        self.pwm.write(0, 0, int(impulsion))
        print(f"setAngleAbsolu({angle}) -> PWM: {int(impulsion)}")

    def reinitialiserRoue(self):
        """
        Réinitialise les roues à la position centrale (0° relatif), c'est-à-dire que les roues sont droites.
        """
        self.pwm.write(0, 0, int(self.centre))
        print(f"reinitialiserRoue() -> PWM: {int(self.centre)}")

    def desactiverPWM(self):
        """
        Désactive la sortie PWM afin de libérer le servo (les roues ne maintiennent plus une position active).
        """
        self.pwm.write(0, 0, 4096)
        print("desactiverPWM() -> PWM désactivé.")

def main():
    """
    Fonction principale pour tester le contrôleur de servo pour les roues :
      1. Réinitialisation des roues au centre (0° relatif, roues droites) et attente 5 secondes.
      2. Rotation des roues vers la droite (+50° relatif) et attente 5 secondes.
      3. Rotation des roues vers la gauche (-50° relatif) et attente 5 secondes.
      4. Réinitialisation finale des roues au centre et désactivation du PWM.
    
    Auteur : Anthony Vergeylen
    Date   : 08-04-2025
    """
    controleur = ControleurServoRoue()
    
    print("\nÉtape 1 : Réinitialisation des roues (roues droites, 0° relatif)")
    controleur.reinitialiserRoue()
    time.sleep(5)
    
    print("\nÉtape 2 : Rotation des roues vers la droite (+50° relatif)")
    controleur.tourner_angle_relatif(50)
    time.sleep(5)
    
    print("\nÉtape 3 : Rotation des roues vers la gauche (-50° relatif)")
    controleur.tourner_angle_relatif(-50)
    time.sleep(5)
    
    print("\nÉtape 4 : Réinitialisation finale des roues (roues droites, 0° relatif)")
    controleur.reinitialiserRoue()
    time.sleep(5)
    
    controleur.desactiverPWM()

if __name__ == "__main__":
    main()
