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
import threading

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
        self.side_threshold = 17         # Seuil pour obstacles latéraux
        self.front_threshold = 30        # Seuil pour alerte obstacle frontal
        self.emergency_threshold = 30    # Seuil pour urgence obstacle frontal

        # Paramètres de virage
        self.angle_virage_gauche = 45
        self.angle_virage_droite = 45
        self.angle_central = 45

        # Durées (en secondes)
        self.duree_virage = 0.3
        self.duree_marche_arriere = 0.4
        self.reverse_pause = 0.5

        # Création des trois capteurs en instanciant la classe CapteurDistance
        max_distance = 1

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

        self.motor_speed_forwards = 20
        self.motor_speed_backwards = 25

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

                time.sleep(0.2)

        except KeyboardInterrupt:
            print("Ctrl+C détecté : arrêt en cours...")
        finally:
            self.cleanup()

    def mode_course(self):
        bobby_speed = True
        #time__of_course = 0 
        # Set the time of one loop to calculate the time of track, instance variable
        # Start sensor threads to continuously update readings
        #self.capteur_front.start_thread()  # Thread for front obstacle detection
        #self.capteur_left.start_thread()       # Thread for left distance measurements
        #self.capteur_right.start_thread()      # Thread for right distance measurements
        #infrared.start_thread(str: "course_mode") # Thread for infrared sensor with course_mode specifically for delay
        #maybe add a true/false variable to make sure about speed varation

        #start_thread(set_timer) # Thread of the timer, set_timer() can be a function of Car
        #basically it increments time_of_course each second
        
        #while infrared.get_status() != 1: # Check constantly if black line not detected 
        while(True):
            if (bobby_speed):
                self.motor_ctrl.forward(self.motor_speed_forwards)   # Maintain moderate speed
            time.sleep(0.1)           # Short delay for sensor updates

            # Obtain the front distance reading
            dist_forward = self.capteur_front.get_distance()

            if (dist_forward >= 20):
                # No immediate obstacle detected: optionally, adjust course gradually
                continue  # Skip the rest of the loop and keep accelerating

            # Obstacle detected; begin braking for more time to decide turning
            self.motor_ctrl.forward(self.motor_speed_backwards*self.acceleration)

            # Get updated lateral sensor readings after braking
            curr_dist_left = self.capteur_left.get_distance()
            curr_dist_right = self.capteur_right.get_distance()

            time.sleep(0.5)
            # If left sensor shows a decreasing distance (i.e. obstacle approaching on left),
            # then turn right
            if (curr_dist_left - self.capteur_left.get_distance() < 0):
                bobby_speed = False
                self.servo_ctrl.setToDegree(self.angle_virage_droite)
                self.motor_ctrl.forward(self.motor_speed_forwards-2) # Small acceleration each time 

            # If right sensor shows a decreasing distance (i.e. obstacle approaching on right),
            # then turn left
            if (curr_dist_right - self.capteur_right.get_distance() < 0):
                bobby_speed = False
                self.servo_ctrl.setToDegree(self.angle_virage_gauche)
                self.motor_ctrl.forward(self.motor_speed_forwards-2) # Small acceleration each time 
            
            bobby_speed = True
            time.sleep(0.5)           # Allow time for the turning maneuver to complete
            self.servo_ctrl.setToDegree(self.angle_central)    # Reset the servo to a straight-ahead position post-maneuver


        time.sleep(2) # 2 Seconds between confirming the black line and stopping. Should be enough to stop after the black line
        self.motor_ctrl.stop() # Stops once the course is finished

        #ultrasound_forward.stop_thread()  # Thread for front obstacle detection stopped
        #ultrasound_left.stop_thread()       # Thread for left distance measurements stopped
        #ultrasound_right.stop_thread()      # Thread for right distance measurements stopped
        #infrared.stop_thread() # Thread for infrared sensor with course_mode specifically for delay stopped
        #time_total = time_of_course #Time stored, can be later displayed
        #stop_thread(set_timer) # Thread of the timer stopped

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
        self.turn_to_most_space_for_forwards_sensor()
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
            print("Plus d'espace à gauche - virage à droite")
            self.servo_ctrl.rotate(self.angle_virage_droite)
        else:
            print("Plus d'espace à droite - virage à gauche")
            self.servo_ctrl.rotate(self.angle_virage_gauche)
        
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)

    def turn_to_most_space_for_forwards_sensor(self):
        """Tourne vers le côté où il y a le plus d'espace disponible pour devant."""
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
        print("On dois rotate de " + str(self.angle_virage_droite))
        self.servo_ctrl.rotate(self.angle_virage_droite)
        time.sleep(self.duree_virage)
        print("on se recentre")
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


    def tour_en_8(self, speed=35):
        """
        Réalise un parcours en forme de 8 (∞) :
        - Un virage à droite en avançant (boucle 1)
        - Puis un virage à gauche en avançant (boucle 2)

        :param speed: Vitesse d’avancement.
        """
        try:
            print("🔁 Début du tour en 8...")

            # 1. Virage à droite
            print("➰ Boucle droite...")
            self.servo_ctrl.rotate(45)
            self.motor_ctrl.forward(speed)
            time.sleep(6)
            self.servo_ctrl.rotate(0)
            time.sleep(4)
            self.servo_ctrl.rotate(45)
            self.motor_ctrl.stop()
            time.sleep(0.5)
            print("✅ Tour en 8 terminé.")
        except Exception as e:
            print("Erreur pendant le tour en 8 :", e)
        finally:
            self.motor_ctrl.stop()
            self.servo_ctrl.disable_pwm()
            print("🛑 Fin de la manœuvre 'tour'")


    def get_distances(self):
        """
        Renvoie les distances actuelles mesurées par les capteurs avant, gauche et droite.
        """
        return {
            "front": round(self.capteur_front.get_distance(), 2),
            "left": round(self.capteur_left.get_distance(), 2),
            "right": round(self.capteur_right.get_distance(), 2)
        }

    def rotation_sur_place(self, duration=5.8, speed=35):
        """
        Simule une rotation continue en avançant avec les roues tournées.
        """
        try:
            print("🔁 Rotation simulée avec virage constant...")
            self.servo_ctrl.rotate(self.angle_virage_droite)  # Direction vers la droite
            self.motor_ctrl.forward(speed)
            self.current_speed = speed / 100 * self.max_speed
            time.sleep(duration)
            self.motor_ctrl.stop()
            time.sleep(0.5)
            self.servo_ctrl.setToDegree(self.angle_central)
            self.current_speed = 0.0
            print("🛑 Rotation terminée (avec virage)")
        except Exception as e:
            print("Erreur pendant la rotation (avec virage) :", e)

    def faire_demi_tour(self, duration=3, speed=35):
        """
        Faire demi tour
        """
        try:
            print("🔁 Rotation simulée avec virage constant...")
            self.servo_ctrl.rotate(self.angle_virage_droite)  # Direction vers la droite
            self.motor_ctrl.forward(speed)
            self.current_speed = speed / 100 * self.max_speed
            time.sleep(duration)
            self.motor_ctrl.stop()
            time.sleep(0.5)
            self.servo_ctrl.setToDegree(self.angle_central)
            self.current_speed = 0.0
            print("🛑 Rotation terminée (avec virage)")
        except Exception as e:
            print("Erreur pendant la rotation (avec virage) :", e)

    
