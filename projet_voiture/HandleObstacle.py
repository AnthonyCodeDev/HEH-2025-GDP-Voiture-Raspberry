#!/usr/bin/env python3
"""
HandleObstacle.py
-----------------
Module de gestion des obstacles pour la voiture autonome.
Ce module est destiné à être appelé dès qu'un obstacle frontal est détecté.
Il effectue les actions suivantes :
  1. Reculer pour prendre de la distance.
  2. Réaliser un crénaut en tournant les roues vers la gauche et en avançant,
     afin de contourner l'obstacle.
  3. Suivre l'obstacle en se basant sur la mesure d'un capteur latéral droit,
     pour s'assurer que le véhicule le contourne correctement.
  4. Réaligner le véhicule en remettant les roues en position centrale une fois
     l'obstacle dépassé.

Auteur : Vergeylen Anthony
Date   : 09-04-2025
"""

import time

# Importation des contrôleurs nécessaires
from ControllerMotor import ControllerMotor
from ControllerServo import ControllerServo
from CapteurDistance import CapteurDistance

class HandleObstacle:
    def __init__(self,
                 motor_speed_backwards=25,
                 motor_speed_forwards=20,
                 side_follow_threshold=20,   # Seuil en cm pour considérer que l'obstacle n'est plus détecté sur le côté droit
                 reverse_duration=0.5,         # Durée en secondes pour la marche arrière
                 crea_duration=0.7,            # Durée en secondes pour la manœuvre latérale (crénaut)
                 forward_duration=0.5,         # Durée en secondes d'avance après réalignement
                 sensor_right_trigger=11,      # Broche GPIO du signal trigger du capteur droit
                 sensor_right_echo=9,          # Broche GPIO du signal echo du capteur droit
                 max_distance=1):              # Distance maximale en mètres détectable par le capteur
        """
        Initialise le module de gestion d'obstacle.

        :param motor_speed_backwards: Vitesse utilisée lors de la marche arrière.
        :param motor_speed_forwards: Vitesse utilisée pour avancer durant le crénaut et le ré-alignement.
        :param side_follow_threshold: Seuil en centimètres pour le suivi de l'obstacle via le capteur droit.
        :param reverse_duration: Temps de marche arrière avant de lancer le crénaut.
        :param crea_duration: Durée de l'avance latérale pour contourner l'obstacle.
        :param forward_duration: Temps d'avance pour réengager la trajectoire droite.
        :param sensor_right_trigger: Broche GPIO pour le trigger du capteur côté droit.
        :param sensor_right_echo: Broche GPIO pour l'echo du capteur côté droit.
        :param max_distance: Distance maximale (en mètres) pour le capteur.
        """
        # Initialisation des contrôleurs des moteurs et du servo
        self.motor_ctrl = ControllerMotor()
        self.servo_ctrl = ControllerServo()
        # Création d'une instance de capteur pour surveiller la distance sur le côté droit
        self.capteur_right = CapteurDistance(trigger=sensor_right_trigger,
                                             echo=sensor_right_echo,
                                             max_distance=max_distance)
        self.motor_speed_backwards = motor_speed_backwards
        self.motor_speed_forwards = motor_speed_forwards
        self.side_follow_threshold = side_follow_threshold
        self.reverse_duration = reverse_duration
        self.crea_duration = crea_duration
        self.forward_duration = forward_duration

        # Réglages du servo :
        # L'angle négatif permet d'orienter les roues vers la gauche
        self.angle_left = -30   # Ajustable selon vos besoins (de -50 à 50)
        # Angle permettant de recentrer les roues (exemple : 45° correspond à une trajectoire droite)
        self.angle_center = 45

    def execute_obstacle_maneuver(self):
        """
        Exécute la manœuvre d'évitement d'obstacle.

        Étapes :
         1. Arrêt et marche arrière pour prendre de la distance.
         2. Tourner les roues vers la gauche et avancer (crénaut) pour contourner l'obstacle.
         3. Surveiller la distance latérale droite pour ajuster la trajectoire.
         4. Une fois l'obstacle passé, remettre les roues en position centrale
            et avancer pour repartir en ligne droite.
        """
        print("Obstacle détecté, exécution de la manœuvre d'évitement...")
        
        # 1. Marche arrière
        print("▶️ Reculer pour prendre de la distance...")
        self.motor_ctrl.stop()
        time.sleep(0.2)
        # La commande backward attend une vitesse négative, d'où le signe négatif
        self.motor_ctrl.backward(-self.motor_speed_backwards)
        time.sleep(self.reverse_duration)
        self.motor_ctrl.stop()
        time.sleep(0.2)
        
        # 2. Crénaut : virage latéral pour contourner l'obstacle
        print("▶️ Exécution du crénaut (virage à gauche)...")
        # Orientation des roues vers la gauche
        self.servo_ctrl.rotate(self.angle_left)
        # Avancer pour contourner l'obstacle
        self.motor_ctrl.forward(self.motor_speed_forwards)
        time.sleep(self.crea_duration)
        self.motor_ctrl.stop()
        time.sleep(0.2)
        
        # 3. Suivi de l'obstacle par le capteur droit
        print("▶️ Suivi de l'obstacle via le capteur droit...")
        distance_right = self.capteur_right.get_distance()
        # Tant que le capteur droit indique que l'obstacle est toujours proche,
        # avancer de petits incréments pour continuer de le contourner.
        while distance_right < self.side_follow_threshold:
            print(f"  ➤ Distance côté droit : {round(distance_right, 2)} cm. Ajustement en cours...")
            self.motor_ctrl.forward(self.motor_speed_forwards)
            time.sleep(0.2)
            self.motor_ctrl.stop()
            time.sleep(0.1)
            distance_right = self.capteur_right.get_distance()
        
        # 4. Réalignement du véhicule pour reprendre une trajectoire droite
        print("▶️ Obstacle contourné, réalignement du véhicule...")
        self.servo_ctrl.setToDegree(self.angle_center)
        # Avancer brièvement pour confirmer la nouvelle direction
        self.motor_ctrl.forward(self.motor_speed_forwards)
        time.sleep(self.forward_duration)
        self.motor_ctrl.stop()
        print("✅ Manœuvre d'évitement terminée. Le véhicule est ré-aligné.")

if __name__ == "__main__":
    # Exemple d'utilisation du module HandleObstacle.
    # Ce code permet de lancer directement la manœuvre d'évitement.
    ho = HandleObstacle()
    ho.execute_obstacle_maneuver()
