#!/usr/bin/env python3

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

        self.side_threshold = 15            # minimum pour considérer qu'il y a un obstacle proche
        self.front_emergency = 20           # arrêt d'urgence
        self.centrage_tolerance = 5         # tolérance en cm pour se dire "au milieu"

        self.angle_central = 45
        self.angle_virage_rapide = 10       # petit angle pour ajustement rapide
        self.duree_ajustement = 0.1         # ajustement très court

        self.motor_speed_forwards = 35
        self.current_speed = 0.0
        self.max_speed = 2.0
        self.acceleration = 0.1

        self.capteur = CapteurDistance()
        self.motor_ctrl = ControllerMotor()
        self.servo_ctrl = ControllerServo()

        self._initialized = True

    def run(self):
        print("🚗 Mode centrage actif : la voiture avance en se maintenant entre les murs.")
        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.servo_ctrl.setToDegree(self.angle_central)

        try:
            while True:
                self.accelerate()
                distances = self.get_distances()

                front = distances["front"]
                left = distances["left"]
                right = distances["right"]

                print(f"Front: {round(front, 2)} cm | Gauche: {round(left, 2)} cm | Droite: {round(right, 2)} cm")

                if front < self.front_emergency:
                    print("🚨 Obstacle frontal ! Arrêt d'urgence.")
                    self.motor_ctrl.stop()
                    self.current_speed = 0
                    break

                self.adjust_to_center(left, right)

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("🛑 Arrêt manuel détecté.")
        finally:
            self.cleanup()

    def accelerate(self):
        if self.current_speed < self.max_speed:
            self.current_speed += self.acceleration
            self.current_speed = min(self.current_speed, self.max_speed)

    def adjust_to_center(self, left, right):
        diff = left - right

        if abs(diff) <= self.centrage_tolerance:
            # On est centré, donc on maintient l'angle droit
            self.servo_ctrl.setToDegree(self.angle_central)
            print("✅ Centrage parfait")
        elif diff > self.centrage_tolerance:
            # Trop proche du mur droit → virage à gauche
            print("↪️ Ajustement vers la gauche")
            self.servo_ctrl.setToDegree(self.angle_central - self.angle_virage_rapide)
            time.sleep(self.duree_ajustement)
        elif diff < -self.centrage_tolerance:
            # Trop proche du mur gauche → virage à droite
            print("↩️ Ajustement vers la droite")
            self.servo_ctrl.setToDegree(self.angle_central + self.angle_virage_rapide)
            time.sleep(self.duree_ajustement)

    def get_distances(self):
        return {
            "front": self.capteur.get_distance_front(),
            "left": self.capteur.get_distance_left(),
            "right": self.capteur.get_distance_right()
        }

    def cleanup(self):
        self.motor_ctrl.stop()
        self.servo_ctrl.disable_pwm()
        GPIO.cleanup()
        print("✅ Nettoyage terminé. Voiture arrêtée.")
