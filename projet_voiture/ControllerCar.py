#!/usr/bin/env python3
"""
ControllerCar.py
----------------
Module modifié pour que, lorsqu'un obstacle est détecté en face,
la voiture recule puis tourne vers le côté disposant de plus d'espace.
"""

import time
from ControllerMotor import ControllerMotor
from ControllerServo import ControllerServo
from CapteurDistance import CapteurDistance
import RPi.GPIO as GPIO

class ControllerCar:
    """
    Contrôleur principal pour la voiture autonome.
    Cette version modifiée recule et effectue un virage vers le côté le plus dégagé
    en cas d'obstacle frontal, plutôt que de simplement avancer de nouveau en ligne droite.
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
        self.front_threshold = 30        # Obstacle frontal (déclenchement du comportement de virage)
        self.emergency_threshold = 10    # Obstacle frontal (cas d'urgence)

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

        # Simulation de la vitesse dynamique
        self.current_speed = 0.0     # Vitesse actuelle en m/s
        self.max_speed = 2.0         # Vitesse maximum simulée en m/s
        self.acceleration = 0.1      # Augmentation m/s par cycle (ajustable)
        self.deceleration = 0.2      # Décélération lors d'une interruption (ajustable)

        self._initialized = True

    def run(self):
        """
        Boucle principale de contrôle autonome.
        En cas d'obstacle frontal (distance < front_threshold), la voiture exécute
        un comportement de recul suivi d'un virage vers le côté le plus dégagé.
        """
        print("Démarrage : la voiture avance en ligne droite...")
        self.motor_ctrl.forward(100)
        self.current_speed = 0.0
        self.servo_ctrl.setToDegree(self.angle_central)

        try:
            while True:
                # Simulation d'une accélération progressive
                if self.current_speed < self.max_speed:
                    self.current_speed += self.acceleration
                    if self.current_speed > self.max_speed:
                        self.current_speed = self.max_speed

                # Lecture des distances
                distance_front = self.capteur.get_distance_front()
                distance_left  = self.capteur.get_distance_left()
                distance_right = self.capteur.get_distance_right()

                print(f"Distances -> Avant: {round(distance_front,2)} cm, Gauche: {round(distance_left,2)} cm, Droite: {round(distance_right,2)} cm, Vitesse: {round(self.current_speed,2)} m/s")

                # Cas obstacle frontal : on recule puis on tourne vers le côté le plus dégagé
                if distance_front < self.front_threshold:
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
        Traite un obstacle frontal en reculant puis en effectuant un virage
        vers le côté où il y a le plus d'espace.

        Le temps de marche arrière est prolongé si l'obstacle est en situation d'urgence.
        """
        # Mesurer la distance frontale en temps réel
        current_distance_front = self.capteur.get_distance_front()
        if current_distance_front < self.emergency_threshold:
            reverse_time = self.duree_marche_arriere * 1.5
            print(f"URGENCE! Obstacle frontal très proche ({round(current_distance_front,2)} cm).")
        else:
            reverse_time = self.duree_marche_arriere
            print(f"Obstacle frontal détecté ({round(current_distance_front,2)} cm).")

        # Phase de recul
        self.motor_ctrl.stop()
        self.current_speed = 0.0
        time.sleep(self.reverse_pause)
        print("Marche arrière pour se dégager de l'obstacle frontal...")
        self.motor_ctrl.backward(-100)
        self.current_speed = -0.5  # Vitesse de recul simulée
        time.sleep(reverse_time)
        self.motor_ctrl.stop()

        # Réévaluation des distances latérales
        distance_left = self.capteur.get_distance_left()
        distance_right = self.capteur.get_distance_right()
        if distance_left >= distance_right:
            print(f"Espace plus grand à gauche ({round(distance_left,2)} cm > {round(distance_right,2)} cm). Virage à gauche.")
            self.servo_ctrl.rotate(self.angle_virage_gauche)
        else:
            print(f"Espace plus grand à droite ({round(distance_right,2)} cm > {round(distance_left,2)} cm). Virage à droite.")
            self.servo_ctrl.rotate(self.angle_virage_droite)

        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)
        self.motor_ctrl.forward(100)
        self.current_speed = self.max_speed  # Reprise de la vitesse

    def handle_double_side_obstacle(self):
        print(f"Obstacle double détecté (G: {round(self.capteur.get_distance_left(),2)} cm, D: {round(self.capteur.get_distance_right(),2)} cm).")
        self.motor_ctrl.backward(-100)
        self.current_speed = 0.0
        time.sleep(self.duree_marche_arriere)
        self.motor_ctrl.forward(100)
        self.servo_ctrl.setToDegree(self.angle_central)
        self.current_speed = self.max_speed

    def handle_left_obstacle(self):
        print(f"Obstacle détecté sur le côté gauche ({round(self.capteur.get_distance_left(),2)} cm). Virage à gauche.")
        # Réduire la vitesse pendant le virage
        self.motor_ctrl.forward(80)
        self.current_speed = 0.5
        self.servo_ctrl.rotate(self.angle_virage_gauche)
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)
        self.motor_ctrl.forward(100)
        self.current_speed = self.max_speed

    def handle_right_obstacle(self):
        print(f"Obstacle détecté sur le côté droit ({round(self.capteur.get_distance_right(),2)} cm). Virage à droite.")
        self.motor_ctrl.forward(80)
        self.current_speed = 0.5
        self.servo_ctrl.rotate(self.angle_virage_droite)
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)
        self.motor_ctrl.forward(100)
        self.current_speed = self.max_speed

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

if __name__ == "__main__":
    controller = ControllerCar()
    controller.run()
