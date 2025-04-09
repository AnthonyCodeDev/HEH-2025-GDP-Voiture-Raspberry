#!/usr/bin/env python3
"""
ControllerCar.py
----------------
Ce module gère le contrôle autonome de la voiture en circuit circulaire.
Il orchestre la lecture des mesures des capteurs de distance (via le module CapteurDistance),
la commande des moteurs et du servo, et le comportement d'évitement des obstacles tout en
suivant automatiquement le tracé circulaire.

Auteur : Vergeylen Anthony
Date   : 08-04-2025 (modifié le 09-04-2025)
Description : Fournit la classe ControllerCar qui utilise CapteurDistance pour obtenir les mesures
              nécessaires à la navigation dans un circuit circulaire.
"""

import time
from ControllerMotor import ControllerMotor
from ControllerServo import ControllerServo
from CapteurDistance import CapteurDistance
import RPi.GPIO as GPIO

class ControllerCar:
    """
    Contrôleur principal pour la voiture autonome sur circuit circulaire.

    La voiture avance automatiquement et suit un tracé circulaire en gardant une distance cible par rapport
    au mur intérieur (supposé être à gauche). Si un obstacle est détecté (avant ou latéralement), la logique d’évitement
    déclenche une série d’actions (arrêt, marche arrière, rotation vers l’espace dégagé) pour sécuriser la trajectoire.
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
        self.side_threshold = 12         # Seuil critique côté
        self.front_threshold = 41        # Seuil d'avertissement frontal
        self.emergency_threshold = 40    # Seuil d'urgence frontal

        # Paramètres de virage pour évitement
        self.angle_virage_gauche = -30
        self.angle_virage_droite = 30
        self.angle_central = 45

        # Durées (en secondes)
        self.duree_virage = 0.4
        self.duree_marche_arriere = 0.35
        self.reverse_pause = 0.5

        # Paramètres du suivi de circuit
        # On suppose que la voiture suit un mur intérieur sur le côté gauche.
        # La voiture essaie de maintenir une distance cible par rapport à ce mur.
        self.target_distance_left = 20.0  # distance idéale à gauche (en cm)
        self.k_p = 1.0                  # gain proportionnel pour la correction de trajectoire

        # Initialisation du module de capteurs de distance
        self.capteur = CapteurDistance()

        # Initialisation des contrôleurs de moteurs et du servo
        self.motor_ctrl = ControllerMotor()
        self.servo_ctrl = ControllerServo()

        # Simulation de la vitesse dynamique
        self.current_speed = 0.0     # vitesse actuelle en m/s
        self.max_speed = 2.0         # vitesse maximum simulée en m/s
        self.acceleration = 0.1      # augmentation m/s par cycle (ajustable)
        self.deceleration = 0.2      # décélération lors d'une interruption (ajustable)

        self.motor_speed_forwards = 35
        self.motor_speed_backwards = 40

        self._initialized = True

    def run(self):
        """
        Lance la boucle principale de contrôle autonome de la voiture en circuit circulaire.

        La voiture démarre en allant de l'avant avec un léger biais de suivi de circuit.
        En l'absence d'obstacles, une correction proportionnelle permet de suivre la trajectoire circulaire.
        En cas de détection d'obstacles, la voiture effectue des manœuvres d'évitement (reculer, tourner,
        reprendre l'avancée).
        """
        print("Démarrage : la voiture suit automatiquement le circuit circulaire...")
        # On démarre avec une commande moteur avant et on centre le servo
        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = 0.0
        self.servo_ctrl.setToDegree(self.angle_central)

        try:
            while True:
                # Simulation d'une accélération progressive vers la vitesse max
                if self.current_speed < self.max_speed:
                    self.current_speed += self.acceleration
                    if self.current_speed > self.max_speed:
                        self.current_speed = self.max_speed

                # Lecture des distances via les capteurs
                distance_front = self.capteur.get_distance_front()
                distance_left  = self.capteur.get_distance_left()
                distance_right = self.capteur.get_distance_right()

                print(f"Distances -> Avant: {round(distance_front,2)} cm, Gauche: {round(distance_left,2)} cm, Droite: {round(distance_right,2)} cm")

                # Gestion des conditions d'urgence et obstacles
                if distance_front < self.emergency_threshold:
                    self.handle_emergency_obstacle()
                elif distance_front < self.front_threshold:
                    self.handle_front_obstacle()
                elif distance_left < self.side_threshold and distance_right < self.side_threshold:
                    self.handle_double_side_obstacle()
                elif distance_left < self.side_threshold:
                    self.handle_left_obstacle()
                elif distance_right < self.side_threshold:
                    self.handle_right_obstacle()
                else:
                    # Aucun obstacle immédiat, on active le suivi de circuit
                    self.follow_circuit()

        except KeyboardInterrupt:
            print("Ctrl+C détecté : arrêt en cours...")
        finally:
            self.cleanup()

    def follow_circuit(self):
        """
        Permet de suivre le circuit circulaire en utilisant la distance du capteur latéral gauche.
        
        On utilise un contrôle proportionnel pour corriger l'orientation :
          - Si la distance mesurée est inférieure à la distance cible, alors la voiture est trop proche
            du mur intérieur et doit tourner vers la droite (angle positif).
          - Si la distance mesurée est supérieure à la distance cible, la voiture est trop loin du mur
            et doit tourner vers la gauche (angle négatif).
        """
        distance_left = self.capteur.get_distance_left()
        # Calcul de l'erreur entre la distance cible et la distance mesurée
        error = self.target_distance_left - distance_left
        # Calcul de l'ajustement de l'angle via le contrôle proportionnel
        steering_adjust = self.k_p * error
        # On limite l'angle à la plage définie par les virages maximum
        steering_adjust = max(min(steering_adjust, self.angle_virage_droite), self.angle_virage_gauche)
        print(f"Suivi de circuit : distance gauche = {round(distance_left,2)} cm, erreur = {round(error,2)}, ajustement = {steering_adjust}°")
        self.servo_ctrl.rotate(steering_adjust)
        # Un court délai pour laisser le temps à la manœuvre (le délai peut être ajusté)
        time.sleep(0.1)
        # On remet le servo en position centrale pour la prochaine correction (cycle de commande)
        self.servo_ctrl.setToDegree(self.angle_central)

    def handle_emergency_obstacle(self):
        """Gère un obstacle frontal en situation d'urgence."""
        distance_front = self.capteur.get_distance_front()
        print(f"URGENCE! Obstacle frontal très proche ({round(distance_front,2)} cm).")
        self.motor_ctrl.stop()
        self.current_speed = 0.0
        time.sleep(0.4)
        self.motor_ctrl.backward(-self.motor_speed_backwards)
        self.current_speed = -0.5  # vitesse de recul simulée
        time.sleep(self.duree_marche_arriere * 1.5)
        self.turn_to_most_space()
        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = self.max_speed  # reprise de la vitesse

    def handle_front_obstacle(self):
        """Gère un obstacle frontal en reculant et en tournant vers le côté le plus dégagé."""
        distance_front = self.capteur.get_distance_front()
        print(f"Obstacle frontal détecté ({round(distance_front,2)} cm).")
        self.motor_ctrl.stop()
        self.current_speed = 0.0
        time.sleep(self.reverse_pause)
        print("Marche arrière pour dégager l'obstacle frontal...")
        self.motor_ctrl.backward(-self.motor_speed_backwards)
        self.current_speed = -0.5
        time.sleep(self.duree_marche_arriere)
        self.turn_to_most_space()
        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = self.max_speed  # reprise de la vitesse

    def turn_to_most_space(self):
        """Tourne vers le côté où il y a le plus d'espace disponible."""
        distance_left = self.capteur.get_distance_left()
        distance_right = self.capteur.get_distance_right()
        
        if distance_left > distance_right:
            print("Plus d'espace à gauche - virage à gauche")
            self.servo_ctrl.rotate(self.angle_virage_gauche)
        else:
            print("Plus d'espace à droite - virage à droite")
            self.servo_ctrl.rotate(self.angle_virage_droite)
        
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)

    def handle_double_side_obstacle(self):
        print(f"Obstacle double détecté (G: {round(self.capteur.get_distance_left(),2)} cm, D: {round(self.capteur.get_distance_right(),2)} cm).")
        self.motor_ctrl.backward(-self.motor_speed_backwards)
        self.current_speed = 0.0
        time.sleep(self.duree_marche_arriere)
        self.turn_to_most_space()
        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = self.max_speed

    def handle_left_obstacle(self):
        print(f"Obstacle détecté sur le côté gauche ({round(self.capteur.get_distance_left(),2)} cm). Virage à gauche.")
        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = 0.5
        self.servo_ctrl.rotate(self.angle_virage_gauche)
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)
        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = self.max_speed

    def handle_right_obstacle(self):
        print(f"Obstacle détecté sur le côté droit ({round(self.capteur.get_distance_right(),2)} cm). Virage à droite.")
        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = 0.5
        self.servo_ctrl.rotate(self.angle_virage_droite)
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)
        self.motor_ctrl.forward(self.motor_speed_forwards)
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

if __name__ == '__main__':
    voiture = ControllerCar()
    voiture.run()
