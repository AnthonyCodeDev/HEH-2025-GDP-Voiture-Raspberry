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
        self.center_val = center   # Valeur PWM pour 0° relatif (position centrale)
        self.min_val = minimum     # Valeur PWM pour -50° relatif
        self.max_val = maximum     # Valeur PWM pour +50° relatif

    def rotate(self, angle):
        """
        Positionne le servo à un angle relatif compris entre -50° et +50°.
        Un angle positif déplace le servo vers la droite, un angle négatif vers la gauche.
        
        :param angle: Angle relatif désiré (entre -50 et +50).
        """
        original_angle = angle
        # Contraindre l'angle dans l'intervalle [-50, 50]
        angle = max(-50, min(50, angle))
        if angle >= 0:
            pulse = self.center_val + ((angle / 50.0) * (self.max_val - self.center_val))
        else:
            pulse = self.center_val + ((angle / 50.0) * (self.center_val - self.min_val))
        # Affichage des informations de débogage
        print(f"rotate({original_angle}) appelé --> Angle contraint: {angle}")
        print(f"Valeurs de base -> Center: {self.center_val}, Min: {self.min_val}, Max: {self.max_val}")
        print(f"Pulse calculé: {pulse} (arrondi: {int(pulse)})")
        self.pwm.write(0, 0, int(pulse))
        print("Commande PWM envoyée.\n")

    def disable_pwm(self):
        """
        Désactive la sortie PWM afin de ne pas maintenir le signal.
        Cela coupe le signal sur le canal PWM pour ne pas forcer le servo à conserver sa position.
        """
        print("Désactivation de la sortie PWM (envoi de la valeur 4096).")
        self.pwm.write(0, 0, 4096)
        print("PWM désactivé.\n")

def main():
    """
    Exécute la séquence de mouvements du servo :
      1. Remet le servo au centre (0° relatif).
      2. Tourne le servo à +50° (droite).
      3. Tourne le servo à -50° (gauche).
      4. Remet le servo au centre.

    Après chaque commande, la sortie PWM est désactivée afin de ne pas maintenir le signal,
    et des informations de débogage sont affichées.
    
    Auteur : Anthony Vergeylen
    Date   : 08-04-2025
    """
    servo = ServoController()
    
    # Réinitialiser le servo à 0° relatif (position centrale)
    print("Réinitialisation : position centrale (0° relatif)")
    servo.rotate(0)
    servo.disable_pwm()
    time.sleep(4)
    
    # Tourner le servo à +50° (droite)
    print("Rotation à +50° (droite)")
    servo.rotate(50)
    servo.disable_pwm()
    time.sleep(4)
    
    # Tourner le servo à -50° (gauche)
    print("Rotation à -50° (gauche)")
    servo.rotate(-50)
    servo.disable_pwm()
    time.sleep(4)
    
    # Remise au centre
    print("Remise finale au centre (0° relatif)")
    servo.rotate(0)
    servo.disable_pwm()

if __name__ == "__main__":
    main()
