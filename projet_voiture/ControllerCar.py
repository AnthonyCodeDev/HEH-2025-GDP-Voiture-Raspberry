#!/usr/bin/env python3
"""
ControllerCar.py
----------------
Ce module gère le contrôle autonome de la voiture.
Il orchestre la lecture des mesures des capteurs (chaque capteur étant une instance de CapteurDistance),
la commande des moteurs et du servo, le comportement d'évitement des obstacles, et deux manœuvres spéciales :
- Rotation sur place
- Tour en 8

Auteur : Vergeylen Anthony
Date   : 08-04-2025
"""

import time, math
from ControllerMotor import ControllerMotor
from ControllerServo import ControllerServo
from CapteurDistance import CapteurDistance
import RPi.GPIO as GPIO

class ControllerCar:
    """
    Contrôleur principal pour la voiture autonome.
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
        self.side_threshold = 12         # Seuil pour obstacles latéraux
        self.front_threshold = 41        # Seuil pour alerte obstacle frontal
        self.emergency_threshold = 40    # Seuil pour urgence obstacle frontal

        # Paramètres de virage
        self.angle_virage_gauche = -30
        self.angle_virage_droite = 30
        self.angle_central = 45

        # Durées (en secondes)
        self.duree_virage = 0.4
        self.duree_marche_arriere = 0.35
        self.reverse_pause = 0.5

        # Création des trois capteurs en instanciant la classe CapteurDistance
        max_distance = 4  # Distance maximale en mètres détectable par les capteurs

        self.capteur_left = CapteurDistance(trigger=26, echo=19, max_distance=max_distance)
        self.capteur_right = CapteurDistance(trigger=11, echo=9, max_distance=max_distance)
        self.capteur_front = CapteurDistance(trigger=6, echo=5, max_distance=max_distance)

        # Initialisation des contrôleurs de moteurs et du servo
        self.motor_ctrl = ControllerMotor()
        self.servo_ctrl = ControllerServo()

        # Simulation de la vitesse dynamique
        self.current_speed = 0.0     # Vitesse actuelle en m/s
        self.max_speed = 2.0         # Vitesse maximale simulée en m/s
        self.acceleration = 0.1      # Accélération (m/s par cycle)
        self.deceleration = 0.2      # Décélération en cas d'interruption

        self._initialized = True

        self.motor_speed_forwards = 35
        self.motor_speed_backwards = 40

    def run(self):
        """
        Lance la boucle principale de contrôle autonome de la voiture.
        """
        print("Démarrage : la voiture avance en ligne droite...")
        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = 0.0
        self.servo_ctrl.setToDegree(self.angle_central)

        try:
            while True:
                # Accélération progressive si aucune perturbation
                if self.current_speed < self.max_speed:
                    self.current_speed += self.acceleration
                    if self.current_speed > self.max_speed:
                        self.current_speed = self.max_speed

                # Lecture des distances à partir des trois capteurs
                distance_front = self.capteur_front.get_distance()
                distance_left  = self.capteur_left.get_distance()
                distance_right = self.capteur_right.get_distance()

                print(f"Distances -> Avant: {round(distance_front, 2)} cm, Gauche: {round(distance_left, 2)} cm, Droite: {round(distance_right, 2)} cm")

                # Gestion des obstacles en fonction des distances mesurées
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

        except KeyboardInterrupt:
            print("Ctrl+C détecté : arrêt en cours...")
        finally:
            self.cleanup()

    def handle_emergency_obstacle(self):
        """Gère un obstacle frontal en situation d'urgence."""
        distance_front = self.capteur_front.get_distance()
        print(f"URGENCE! Obstacle frontal très proche ({round(distance_front, 2)} cm).")
        self.motor_ctrl.stop()
        self.current_speed = 0.0
        time.sleep(0.4)
        self.motor_ctrl.backward(-self.motor_speed_backwards)
        self.current_speed = -0.5  # Vitesse de recul simulée
        time.sleep(self.duree_marche_arriere * 1.5)
        self.turn_to_most_space()
        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = self.max_speed  # Reprise de la vitesse

    def handle_front_obstacle(self):
        """Gère un obstacle frontal en reculant et en tournant vers le côté le plus dégagé."""
        distance_front = self.capteur_front.get_distance()
        print(f"Obstacle frontal détecté ({round(distance_front, 2)} cm).")
        self.motor_ctrl.stop()
        self.current_speed = 0.0
        time.sleep(self.reverse_pause)
        print("Marche arrière pour dégager l'obstacle frontal...")
        self.motor_ctrl.backward(-self.motor_speed_backwards)
        self.current_speed = -0.5
        time.sleep(self.duree_marche_arriere)
        self.turn_to_most_space()
        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = self.max_speed  # Reprise de la vitesse

    def turn_to_most_space(self):
        """Tourne vers le côté où il y a le plus d'espace disponible."""
        distance_left = self.capteur_left.get_distance()
        distance_right = self.capteur_right.get_distance()
        
        if distance_left > distance_right:
            print("Plus d'espace à gauche - virage à gauche")
            self.servo_ctrl.rotate(self.angle_virage_gauche)
        else:
            print("Plus d'espace à droite - virage à droite")
            self.servo_ctrl.rotate(self.angle_virage_droite)
        
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)

    def handle_double_side_obstacle(self):
        distance_left = self.capteur_left.get_distance()
        distance_right = self.capteur_right.get_distance()
        print(f"Obstacle double détecté (Gauche: {round(distance_left, 2)} cm, Droite: {round(distance_right, 2)} cm).")
        self.motor_ctrl.backward(-self.motor_speed_backwards)
        self.current_speed = 0.0
        time.sleep(self.duree_marche_arriere)
        self.turn_to_most_space()
        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = self.max_speed

    def handle_left_obstacle(self):
        distance_left = self.capteur_left.get_distance()
        print(f"Obstacle détecté sur le côté gauche ({round(distance_left, 2)} cm). Virage à gauche.")
        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = 0.5
        self.servo_ctrl.rotate(self.angle_virage_gauche)
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)
        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = self.max_speed

    def handle_right_obstacle(self):
        distance_right = self.capteur_right.get_distance()
        print(f"Obstacle détecté sur le côté droit ({round(distance_right, 2)} cm). Virage à droite.")
        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = 0.5
        self.servo_ctrl.rotate(self.angle_virage_droite)
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)
        self.motor_ctrl.forward(self.motor_speed_forwards)
        self.current_speed = self.max_speed

    def restart_car(self):
        """
        Redémarre le module : arrêt des moteurs, remise de la vitesse à 0 et réinitialisation de la position du servo.
        Le module est ensuite en attente d'une commande de démarrage (LED verte ou bouton start).
        """
        print("🔄 Redémarrage du module (restart_car) en cours...")
        # Arrêt en douceur des moteurs
        self.motor_ctrl.stop()
        self.current_speed = 0.0

        try:
            # Séquence d'initialisation du servo (similaire à celle du main.py)
            self.servo_ctrl.setToDegree(self.angle_central)
            time.sleep(0.3)
            self.servo_ctrl.setToDegree(0)
            time.sleep(0.3)
            self.servo_ctrl.setToDegree(self.angle_central)
            time.sleep(0.3)
            self.servo_ctrl.setToDegree(90)
            time.sleep(0.3)
            self.servo_ctrl.setToDegree(self.angle_central)
            time.sleep(0.3)
            self.servo_ctrl.disable_pwm()
        except Exception as e:
            print("Erreur lors de la réinitialisation du servo dans restart_car :", e)

        print("🔄 Module relancé, en attente d'une commande de démarrage (LED verte ou bouton start).")

    def cleanup(self):
        self.motor_ctrl.stop()
        self.servo_ctrl.disable_pwm()
        GPIO.cleanup()
        print("Nettoyage des GPIO terminé. La voiture est arrêtée.")

    def get_speed(self):
        """
        Renvoie la vitesse actuelle du véhicule en m/s.
        """
        return self.current_speed

    def rotation_sur_place(self, duration=10, speed=100):
        """
        Fait tourner la voiture sur elle-même (rotation différentielle) pendant une durée donnée.
        Un moteur est commandé en avant et l'autre en arrière.
        
        :param duration: Durée de la rotation en secondes (par défaut 10).
        :param speed: Vitesse de rotation (0 à 100).
        
        Attention : cette méthode utilise les attributs internes du moteur (précédés de __)
        et réalise une gestion directe. Assurez-vous que cela correspond à votre implémentation.
        """
        try:
            print("🔁 Rotation sur place...")
            pwm_val = self.motor_ctrl._MotorController__scale_speed(speed)
            self.motor_ctrl._MotorController__apply_motor_state(
                self.motor_ctrl._MotorController__moteur0_pin_a,
                self.motor_ctrl._MotorController__moteur0_pin_b,
                pwm_val
            )
            self.motor_ctrl._MotorController__apply_motor_state(
                self.motor_ctrl._MotorController__moteur1_pin_a,
                self.motor_ctrl._MotorController__moteur1_pin_b,
                -pwm_val
            )
            time.sleep(duration)
            print("🛑 Arrêt du mouvement")
            self.motor_ctrl.stop()
        except Exception as e:
            print("Erreur pendant la rotation sur place :", e)

    def tour_en_8(self, speed=35, cycle_time=12, dt=0.03, cycles=3, amplitude=20):
        """
        Réalise un parcours en 8.
        
        Pendant chaque cycle, le servo module sa position en fonction d'une fonction sinusoïdale,
        ce qui crée une trajectoire en 8 lorsque la voiture avance.
        
        :param speed: Vitesse de déplacement pendant le 8.
        :param cycle_time: Durée d'un cycle complet (influence la fréquence des oscillations).
        :param dt: Intervalle de temps entre deux mises à jour du servo.
        :param cycles: Nombre de cycles (8) à réaliser.
        :param amplitude: Amplitude de l'oscillation du servo (en degrés).
        """
        try:
            print("🎯 Lancement du parcours en 8...")
            for _ in range(cycles):
                start = time.time()
                while time.time() - start < cycle_time:
                    t = time.time() - start
                    # Calcule l'angle du servo : position centrale 45° modulée par une sinusoïde.
                    angle = 45 + amplitude * math.sin(2 * math.pi * t / cycle_time)
                    self.servo_ctrl.setToDegree(angle)
                    self.motor_ctrl.forward(speed)
                    time.sleep(dt)
            self.motor_ctrl.stop()
            self.servo_ctrl.setToDegree(45)
            print("✅ Parcours en 8 terminé.")
        except Exception as e:
            print("Erreur pendant le tour en 8 :", e)
        finally:
            self.motor_ctrl.stop()
            self.servo_ctrl.disable_pwm()
            print("Fin de la manœuvre 'tour en 8'.")
