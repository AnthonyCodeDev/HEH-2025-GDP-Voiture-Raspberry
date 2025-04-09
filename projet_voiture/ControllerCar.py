#!/usr/bin/env python3
"""
ControllerCar.py
----------------
Ce module gère le contrôle autonome de la voiture.
Il orchestre la lecture des mesures des capteurs de distance (via le module CapteurDistance),
la commande des moteurs et du servo, et le comportement d'évitement des obstacles.

Auteur : Vergeylen Anthony
Date   : 08-04-2025
Quoi   : Fournit la classe ControllerCar qui utilise CapteurDistance pour obtenir les mesures nécessaires à la navigation.
"""

import time
from ControllerMotor import ControllerMotor
from ControllerServo import ControllerServo
from CapteurDistance import CapteurDistance
import RPi.GPIO as GPIO

class ControllerCar:
    """
    Contrôleur principal pour la voiture autonome.

    QUI : Vergeylen Anthony
    QUAND : 08-04-2025
    QUOI : Surveille les mesures de distance fournies par les capteurs (via CapteurDistance)
           et commande les moteurs et le servo pour éviter les obstacles.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ControllerCar, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Empêcher la réinitialisation multiple de l'instance (singleton)
        if hasattr(self, '_initialized') and self._initialized:
            return

        # Seuils de détection en cm
        self.side_threshold = 15         # Obstacle latéral
        self.front_threshold = 30        # Obstacle frontal (avertissement)
        self.emergency_threshold = 10    # Obstacle frontal (urgence)

        # Paramètres de virage
        self.angle_virage_gauche = -22.5
        self.angle_virage_droite = 45
        self.angle_central = 45

        # Durées (en secondes)
        self.duree_virage = 3
        self.duree_marche_arriere = 1
        self.reverse_pause = 0.5

        # Initialisation du module de capteurs de distance
        self.capteur = CapteurDistance()

        # Initialisation des contrôleurs de moteurs et du servo
        self.motor_ctrl = ControllerMotor()
        self.servo_ctrl = ControllerServo()

        self._initialized = True

    def run(self):
        """
        Lance la boucle principale de contrôle autonome de la voiture.

        QUI : Vergeylen Anthony
        QUAND : 08-04-2025
        QUOI : Démarre le mouvement en avant et surveille en continu les mesures des capteurs
               pour déclencher les manœuvres d'évitement en cas d'obstacle.
        """
        print("Démarrage : la voiture avance en ligne droite...")
        self.motor_ctrl.forward(100)
        self.servo_ctrl.setToDegree(self.angle_central)

        try:
            while True:
                distance_front = self.capteur.get_distance_front()
                distance_left  = self.capteur.get_distance_left()
                distance_right = self.capteur.get_distance_right()

                print(f"Distances -> Avant: {round(distance_front,2)} cm, Gauche: {round(distance_left,2)} cm, Droite: {round(distance_right,2)} cm")

                if distance_front < self.emergency_threshold:
                    print(f"URGENCE! Obstacle frontal très proche ({round(distance_front,2)} cm). Arrêt immédiat.")
                    self.motor_ctrl.stop()
                    time.sleep(0.5)
                    self.motor_ctrl.backward(-100)
                    time.sleep(self.duree_marche_arriere * 1.5)
                    self.motor_ctrl.forward(100)
                    self.servo_ctrl.setToDegree(self.angle_central)
                elif distance_front < self.front_threshold:
                    self.handle_front_obstacle()
                elif distance_left < self.side_threshold and distance_right < self.side_threshold:
                    self.handle_double_side_obstacle()
                elif distance_left < self.side_threshold:
                    self.handle_left_obstacle()
                elif distance_right < self.side_threshold:
                    self.handle_right_obstacle()
                    
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Ctrl+C détecté : arrêt en cours...")
        finally:
            self.cleanup()

    def handle_front_obstacle(self):
        """
        Gère l'évitement d'un obstacle frontal.

        QUI : Vergeylen Anthony
        QUOI : Arrête, recule brièvement et déclenche un virage en fonction des mesures latérales.
        """
        distance_left = self.capteur.get_distance_left()
        distance_right = self.capteur.get_distance_right()
        print(f"Obstacle frontal détecté ({round(self.capteur.get_distance_front(),2)} cm). Arrêt immédiat.")
        self.motor_ctrl.stop()
        time.sleep(self.reverse_pause)
        print("Marche arrière pour dégager l'obstacle frontal...")
        self.motor_ctrl.backward(-100)
        time.sleep(self.duree_marche_arriere)
        self.motor_ctrl.forward(100)
        distance_left = self.capteur.get_distance_left()
        distance_right = self.capteur.get_distance_right()
        if distance_left > distance_right:
            print(f"Plus de clearance à gauche (G: {round(distance_left,2)} cm, D: {round(distance_right,2)} cm). Virage à gauche.")
            self.servo_ctrl.rotate(self.angle_virage_gauche)
        else:
            print(f"Plus de clearance à droite (G: {round(distance_left,2)} cm, D: {round(distance_right,2)} cm). Virage à droite.")
            self.servo_ctrl.rotate(self.angle_virage_droite)
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)

    def handle_double_side_obstacle(self):
        """
        Gère la présence simultanée d'obstacles sur les deux côtés.

        QUI : Vergeylen Anthony
        QUOI : Recule puis effectue un virage selon la disponibilité d'un côté dégagé.
        """
        print(f"Obstacle double détecté (G: {round(self.capteur.get_distance_left(),2)} cm, D: {round(self.capteur.get_distance_right(),2)} cm). Marche arrière...")
        self.motor_ctrl.backward(-100)
        time.sleep(self.duree_marche_arriere)
        self.motor_ctrl.forward(100)
        while (self.capteur.get_distance_left() < self.side_threshold and
               self.capteur.get_distance_right() < self.side_threshold):
            time.sleep(0.1)
        distance_left = self.capteur.get_distance_left()
        distance_right = self.capteur.get_distance_right()
        if distance_left >= self.side_threshold and distance_right < self.side_threshold:
            print(f"Côté gauche dégagé (G: {round(distance_left,2)} cm). Virage à gauche.")
            self.servo_ctrl.rotate(self.angle_virage_gauche)
        elif distance_right >= self.side_threshold and distance_left < self.side_threshold:
            print(f"Côté droit dégagé (D: {round(distance_right,2)} cm). Virage à droite.")
            self.servo_ctrl.rotate(self.angle_virage_droite)
        else:
            if distance_left > distance_right:
                print(f"Les deux côtés dégagés (G: {round(distance_left,2)} cm, D: {round(distance_right,2)} cm). Virage à gauche.")
                self.servo_ctrl.rotate(self.angle_virage_gauche)
            else:
                print(f"Les deux côtés dégagés (G: {round(distance_left,2)} cm, D: {round(distance_right,2)} cm). Virage à droite.")
                self.servo_ctrl.rotate(self.angle_virage_droite)
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)

    def handle_left_obstacle(self):
        """
        Gère l'évitement d'un obstacle sur le côté gauche.

        QUI : Vergeylen Anthony
        QUOI : Effectue un virage à gauche.
        """
        print(f"Obstacle détecté sur le côté gauche ({round(self.capteur.get_distance_left(),2)} cm). Virage à gauche.")
        self.servo_ctrl.rotate(self.angle_virage_gauche)
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)

    def handle_right_obstacle(self):
        """
        Gère l'évitement d'un obstacle sur le côté droit.

        QUI : Vergeylen Anthony
        QUOI : Effectue un virage à droite.
        """
        print(f"Obstacle détecté sur le côté droit ({round(self.capteur.get_distance_right(),2)} cm). Virage à droite.")
        self.servo_ctrl.rotate(self.angle_virage_droite)
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)

    def cleanup(self):
        """
        Arrête les moteurs, désactive le PWM du servo et nettoie les GPIO.

        QUI : Vergeylen Anthony
        QUOI : Libère les ressources et effectue un arrêt propre.
        """
        self.motor_ctrl.stop()
        self.servo_ctrl.disable_pwm()
        GPIO.cleanup()
        print("Nettoyage des GPIO terminé. La voiture est arrêtée.")
