#!/usr/bin/env python3
"""
ControllerCar.py
----------------
Ce module gère le contrôle autonome de la voiture.
Il orchestre la lecture des mesures des capteurs de distance (via le module CapteurDistance),
la commande des moteurs et du servo, et le comportement d'évitement des obstacles.
Il simule également une vitesse dynamique qui s'ajuste de manière fluide en fonction des actions.

Auteur : Vergeylen Anthony
Date   : 08-04-2025 (modifié le 09-04-2025)
Quoi   : Fournit la classe ControllerCar qui utilise CapteurDistance pour obtenir les mesures nécessaires
         à la navigation et simule une vitesse variable en m/s.
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
    QUOI: Surveille les mesures de distance fournies par les capteurs et commande
           les moteurs et le servo pour éviter les obstacles, tout en simulant la vitesse dynamique.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ControllerCar, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return

        # Seuils de détection (en cm)
        self.side_threshold = 15         # Obstacle latéral
        self.front_threshold = 30        # Obstacle frontal (avertissement)
        self.emergency_threshold = 10    # Obstacle frontal (urgence)

        # Paramètres de virage (en degrés)
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

        # Simulation de la vitesse dynamique (en m/s)
        self.current_speed = 0.0          # vitesse actuelle en m/s
        self.max_speed = 2.0              # vitesse maximum simulée en m/s (à 100% de puissance)
        self.acceleration_rate = 0.1      # accroissement de la vitesse par cycle (m/s)
        self.deceleration_rate = 0.1      # réduction de la vitesse par cycle (m/s)

        self._initialized = True

    def run(self):
        """
        Lance la boucle principale de contrôle autonome de la voiture.
        Simule une accélération progressive et ajuste la vitesse en fonction des obstacles et virages.
        """
        print("Démarrage : la voiture avance en ligne droite...")
        self.motor_ctrl.forward(100)
        self.current_speed = 0.0
        self.servo_ctrl.setToDegree(self.angle_central)

        try:
            while True:
                # Simulation d'une accélération progressive
                if self.current_speed < self.max_speed:
                    self.current_speed += self.acceleration_rate
                    if self.current_speed > self.max_speed:
                        self.current_speed = self.max_speed

                # Lecture des distances
                distance_front = self.capteur.get_distance_front()
                distance_left  = self.capteur.get_distance_left()
                distance_right = self.capteur.get_distance_right()

                print(f"Distances -> Avant: {round(distance_front,2)} cm, Gauche: {round(distance_left,2)} cm, Droite: {round(distance_right,2)} cm, Vitesse: {round(self.current_speed,2)} m/s")

                # S'il y a un obstacle devant (urgent ou avertissement), on effectue un virage
                if distance_front < self.emergency_threshold or distance_front < self.front_threshold:
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

    def smooth_decelerate(self, target_speed):
        """
        Décélère progressivement la vitesse jusqu'à target_speed.
        """
        while self.current_speed > target_speed:
            self.current_speed -= self.deceleration_rate
            if self.current_speed < target_speed:
                self.current_speed = target_speed
            time.sleep(0.1)
            print(f"Décélération: Vitesse = {round(self.current_speed,2)} m/s")

    def smooth_accelerate(self, target_speed):
        """
        Accélère progressivement la vitesse jusqu'à target_speed.
        """
        while self.current_speed < target_speed:
            self.current_speed += self.acceleration_rate
            if self.current_speed > target_speed:
                self.current_speed = target_speed
            time.sleep(0.1)
            print(f"Accélération: Vitesse = {round(self.current_speed,2)} m/s")

    def handle_front_obstacle(self):
        """
        Gère l'évitement d'un obstacle frontal.
        Au lieu de repartir tout droit après un recul, la voiture tourne vers le côté offrant le plus de clearance.
        """
        distance_front = self.capteur.get_distance_front()
        print(f"Obstacle frontal détecté ({round(distance_front,2)} cm).")
        # Décélération progressive jusqu'à 0
        self.smooth_decelerate(0)
        self.motor_ctrl.stop()
        time.sleep(self.reverse_pause)

        print("Marche arrière pour dégager l'obstacle frontal...")
        self.motor_ctrl.backward(-100)
        self.current_speed = 0.0  # Après le recul, vitesse nulle
        time.sleep(self.duree_marche_arriere)

        # Choix du virage selon la clearance latérale
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
        self.motor_ctrl.forward(100)
        # Accélération progressive jusqu'à la vitesse max
        self.smooth_accelerate(self.max_speed)

    def handle_double_side_obstacle(self):
        """
        Gère la présence simultanée d'obstacles sur les deux côtés.
        La voiture recule et, dès qu'un côté se libère, effectue le virage correspondant.
        """
        print(f"Obstacle double détecté (G: {round(self.capteur.get_distance_left(),2)} cm, D: {round(self.capteur.get_distance_right(),2)} cm).")
        self.smooth_decelerate(0)
        self.motor_ctrl.backward(-100)
        self.current_speed = 0.0
        time.sleep(self.duree_marche_arriere)
        self.motor_ctrl.forward(100)
        self.servo_ctrl.setToDegree(self.angle_central)
        self.smooth_accelerate(self.max_speed)

    def handle_left_obstacle(self):
        """
        Gère l'évitement d'un obstacle sur le côté gauche.
        La voiture réduit sa vitesse, effectue un virage à gauche, puis reprend de la vitesse.
        """
        print(f"Obstacle détecté sur le côté gauche ({round(self.capteur.get_distance_left(),2)} cm). Virage à gauche.")
        self.smooth_decelerate(0.5)
        self.motor_ctrl.forward(80)
        self.current_speed = 0.5
        self.servo_ctrl.rotate(self.angle_virage_gauche)
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)
        self.motor_ctrl.forward(100)
        self.smooth_accelerate(self.max_speed)

    def handle_right_obstacle(self):
        """
        Gère l'évitement d'un obstacle sur le côté droit.
        La voiture ralentit, effectue un virage à droite, puis reprend sa vitesse.
        """
        print(f"Obstacle détecté sur le côté droit ({round(self.capteur.get_distance_right(),2)} cm). Virage à droite.")
        self.smooth_decelerate(0.5)
        self.motor_ctrl.forward(80)
        self.current_speed = 0.5
        self.servo_ctrl.rotate(self.angle_virage_droite)
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)
        self.motor_ctrl.forward(100)
        self.smooth_accelerate(self.max_speed)

    def cleanup(self):
        self.motor_ctrl.stop()
        self.servo_ctrl.disable_pwm()
        GPIO.cleanup()
        print("Nettoyage des GPIO terminé. La voiture est arrêtée.")

    def get_distances(self):
        return {
            "front": self.capteur.get_distance_front(),
            "left": self.capteur.get_distance_left(),
            "right": self.capteur.get_distance_right()
        }
    
    def get_speed(self):
        """
        Renvoie la vitesse actuelle du véhicule en m/s.
        """
        return self.current_speed
