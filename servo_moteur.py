#!/usr/bin/env python3
import PCA9685 as PCA
import time

class ControleurServo:
    """
    Contrôleur de servo pour la direction des roues.
    
    Cette classe permet de positionner les roues en fonction d'un angle de rotation.
    
    Deux modes de contrôle sont disponibles :
      - Un ajustement par angle relatif : l'angle est spécifié entre -50° (gauche extrême) et +50° (droite extrême) par rapport à la position centrale.
      - Un positionnement par angle absolu : l'angle est spécifié dans une plage de 0° à 180°, où 0° correspond à la position centrée.
    
    Les valeurs PWM associées aux positions sont déterminées lors de l'initialisation :
      - pwm_centre   : valeur PWM pour la position centrée (roues droites).
      - pwm_minimum  : valeur PWM pour l'angle relatif le plus négatif (-50°).
      - pwm_maximum  : valeur PWM pour l'angle relatif le plus positif (+50°).
    
    Auteur : Anthony Vergeylen
    Date   : 08-04-2025
    """
    def __init__(self, pwm_centre=320, pwm_minimum=200, pwm_maximum=500):
        """
        Initialise le contrôleur du servo en configurant la fréquence PWM et les limites de position.
        
        :param pwm_centre: Valeur PWM correspondant à la position centrée (0° relatif).
        :param pwm_minimum: Valeur PWM pour le point extrême gauche (-50° relatif).
        :param pwm_maximum: Valeur PWM pour le point extrême droite (+50° relatif).
        """
        self.pwm = PCA.PWM()
        self.pwm.frequency = 60
        self.pwm_centre = pwm_centre
        self.pwm_minimum = pwm_minimum
        self.pwm_maximum = pwm_maximum

    def ajuster_angle_relatif(self, angle_relatif):
        """
        Positionne les roues à un angle relatif donné.
        
        La plage d'angles relative est contrainte entre -50° et +50°.
        - Un angle positif oriente les roues vers la droite.
        - Un angle négatif oriente les roues vers la gauche.
        
        Le calcul du signal PWM est effectué en interpolant entre la valeur centrale et
        la valeur minimum ou maximum selon l'orientation demandée.
        
        :param angle_relatif: Angle relatif désiré (entre -50 et 50 degrés).
        """
        # Contrainte de l'angle dans l'intervalle [-50, 50]
        angle_relatif = max(-50, min(50, angle_relatif))
        if angle_relatif >= 0:
            pwm_signal = self.pwm_centre + ((angle_relatif / 50.0) * (self.pwm_maximum - self.pwm_centre))
        else:
            pwm_signal = self.pwm_centre + ((angle_relatif / 50.0) * (self.pwm_centre - self.pwm_minimum))
        self.pwm.write(0, 0, int(pwm_signal))
        print(f"ajuster_angle_relatif({angle_relatif}) -> PWM: {int(pwm_signal)}")

    def positionner_angle_absolu(self, angle_absolu):
        """
        Positionne les roues à un angle absolu spécifié.
        
        L'angle absolu doit être compris entre 0° et 180°, où 0° correspond à la position
        centrée (0° relatif). Le signal PWM est alors interpolé sur toute la plage définie
        par pwm_minimum et pwm_maximum.
        
        :param angle_absolu: Angle absolu désiré (entre 0 et 180 degrés).
        """
        # Contrainte de l'angle dans l'intervalle [0, 180]
        angle_absolu = max(0, min(180, angle_absolu))
        pwm_signal = self.pwm_centre + ((angle_absolu / 180.0) * (self.pwm_maximum - self.pwm_minimum))
        self.pwm.write(0, 0, int(pwm_signal))
        print(f"positionner_angle_absolu({angle_absolu}) -> PWM: {int(pwm_signal)}")

    def remettre_roues_droites(self):
        """
        Ramène les roues à la position centrée (droites).
        
        La commande force le signal PWM à la valeur centrale calibrée, garantissant une orientation rectiligne.
        """
        self.pwm.write(0, 0, int(self.pwm_centre))
        print(f"remettre_roues_droites() -> PWM: {int(self.pwm_centre)}")

    def desactiver_pwm(self):
        """
        Désactive le signal PWM afin de libérer le servo.
        
        Cette opération permet d'arrêter le maintien de la position par le servo, rendant ainsi
        le système non actif jusqu'à une nouvelle commande.
        """
        self.pwm.write(0, 0, 4096)
        print("Signal PWM désactivé.")

def tester_controleur_moteur():
    """
    Fonction principale pour tester le contrôleur de moteurs/servos.
    
    Le test consiste à :
      1. Positionner les roues vers l'extrême droite pendant environ 2 secondes.
      2. Positionner ensuite les roues vers l'extrême gauche pendant environ 2 secondes.
      3. Remettre les roues en position droite (centrée).
      4. Désactiver le signal PWM.
    
    Auteur : Anthony Vergeylen
    Date   : 08-04-2025
    Quoi   : Test du fonctionnement et du réajustement du contrôleur de moteurs.
    """
    controleur_servo = ControleurServo()

    # Faire tourner les roues vers la droite (angle absolu positif proche de la valeur maximale)
    print("Orientation vers la droite...")
    controleur_servo.positionner_angle_absolu(180)
    time.sleep(2)

    # Faire tourner les roues vers la gauche.
    # Pour simuler la rotation vers la gauche, nous utilisons ici un angle absolu faible (proche de 0, la position centrée)
    # L'interprétation exacte dépend de la calibration du servo.
    print("Orientation vers la gauche...")
    controleur_servo.positionner_angle_absolu(0)
    time.sleep(2)

    # Remettre les roues en position droite (centrée)
    print("Remise en position droite...")
    controleur_servo.remettre_roues_droites()

    # Désactivation du signal PWM
    controleur_servo.desactiver_pwm()

if __name__ == "__main__":
    tester_controleur_moteur()
