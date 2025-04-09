#!/usr/bin/env python3
"""
ControllerCar.py
----------------
Ce module gère le contrôle autonome de la voiture.
Il orchestre la lecture des mesures des capteurs de distance,
la commande des moteurs et du servo, et le comportement d'évitement des obstacles.

Auteur : Vergeylen Anthony
Date   : 08-04-2025
"""

import time
import RPi.GPIO as GPIO
from ControllerMotor import ControllerMotor
from ControllerServo import ControllerServo
from CapteurDistance import CapteurDistance

class ControllerCar:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ControllerCar, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return

        # Seuils
        self.side_threshold = 20
        self.front_threshold = 35
        self.emergency_threshold = 20

        # Paramètres de virage
        self.angle_virage_gauche = -34
        self.angle_virage_droite = 34
        self.angle_central = 45

        # Durées
        self.duree_virage = 0.5
        self.duree_marche_arriere = 0.35
        self.reverse_pause = 0.3

        # Contrôleurs
        self.capteur = CapteurDistance()
        self.motor_ctrl = ControllerMotor()
        self.servo_ctrl = ControllerServo()

        # Vitesse
        self.current_speed = 0.0
        self.max_speed = 2.0
        self.acceleration = 0.1
        self.deceleration = 0.2

        # Motor speeds
        self.motor_speed_forwards = 35
        self.motor_speed_backwards = 40

        self._initialized = True

    def run(self):
        print("🚗 La voiture démarre en ligne droite.")
        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.servo_ctrl.setToDegree(self.angle_central)

        try:
            while True:
                self.accelerate()
                distances = self.get_distances()
                print(f"Distances → Avant: {round(distances['front'], 2)} cm | Gauche: {round(distances['left'], 2)} cm | Droite: {round(distances['right'], 2)} cm")

                if distances['front'] < self.emergency_threshold:
                    self.handle_emergency_obstacle()
                elif distances['front'] < self.front_threshold:
                    self.handle_front_obstacle()
                elif distances['left'] < self.side_threshold and distances['right'] < self.side_threshold:
                    self.handle_double_side_obstacle()
                elif distances['left'] < self.side_threshold:
                    self.handle_side_obstacle('left')
                elif distances['right'] < self.side_threshold:
                    self.handle_side_obstacle('right')

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("🛑 Arrêt manuel détecté.")
        finally:
            self.cleanup()

    def accelerate(self):
        if self.current_speed < self.max_speed:
            self.current_speed += self.acceleration
            self.current_speed = min(self.current_speed, self.max_speed)

    def handle_emergency_obstacle(self):
        print("🚨 URGENCE : Obstacle trop proche devant.")
        self.motor_ctrl.stop()
        self.current_speed = 0.0
        time.sleep(0.2)

        self.motor_ctrl.backward(-self.motor_speed_backwards)
        time.sleep(self.duree_marche_arriere * 1.5)
        self.motor_ctrl.stop()

        self.turn_to_most_space()

        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = self.max_speed

    def handle_front_obstacle(self):
        print("⚠️ Obstacle frontal détecté.")
        self.motor_ctrl.stop()
        self.current_speed = 0.0
        time.sleep(self.reverse_pause)

        self.motor_ctrl.backward(-self.motor_speed_backwards)
        time.sleep(self.duree_marche_arriere)
        self.motor_ctrl.stop()

        self.turn_to_most_space()

        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = self.max_speed

    def handle_double_side_obstacle(self):
        print("⛔ Obstacle des deux côtés détecté.")
        self.motor_ctrl.backward(-self.motor_speed_backwards)
        time.sleep(self.duree_marche_arriere)
        self.motor_ctrl.stop()

        self.turn_to_most_space()

        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = self.max_speed

    def handle_side_obstacle(self, side):
        dist = self.capteur.get_distance_left() if side == 'left' else self.capteur.get_distance_right()
        print(f"⬅️ Obstacle {side} détecté ({round(dist,2)} cm). Recul puis virage opposé.")

        self.motor_ctrl.backward(-self.motor_speed_backwards * 0.6)
        time.sleep(self.duree_marche_arriere)
        self.motor_ctrl.stop()

        if side == 'left':
            self.servo_ctrl.rotate(self.angle_virage_droite)
        else:
            self.servo_ctrl.rotate(self.angle_virage_gauche)

        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)

        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = self.max_speed

    def turn_to_most_space(self):
        left = self.capteur.get_distance_left()
        right = self.capteur.get_distance_right()
        direction = 'gauche' if left > right else 'droite'
        print(f"🔄 Virage vers la {direction}")

        angle = self.angle_virage_gauche if left > right else self.angle_virage_droite
        self.servo_ctrl.rotate(angle)
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)

    def get_distances(self):
        return {
            "front": self.capteur.get_distance_front(),
            "left": self.capteur.get_distance_left(),
            "right": self.capteur.get_distance_right()
        }

    def get_speed(self):
        return self.current_speed

    def cleanup(self):
        self.motor_ctrl.stop()
        self.servo_ctrl.disable_pwm()
        GPIO.cleanup()
        print("✅ GPIO nettoyés. Voiture arrêtée.")
