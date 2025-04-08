#!/usr/bin/env python3
"""
go.py
------
Ce script commande la voiture pour qu'elle avance indéfiniment et évite les obstacles grâce à trois capteurs ultrason :

    - Capteur gauche (trig 26 / echo 19) : Si la distance est inférieure à 15 cm, tourner à gauche.
    - Capteur droit (trig 11 / echo 9)    : Si la distance est inférieure à 15 cm, tourner à droite.
    - Capteur avant (trig 6 / echo 5)     : Si la distance est inférieure à 30 cm (15 cm + marge), 
      arrêter, reculer, puis choisir la direction offrant le plus de clearance pour repartir.

Après chaque manœuvre d'évitement, les roues sont remises au point mort (45°).  
Lors d'une interruption clavier (Ctrl+C), le programme arrête proprement les moteurs, désactive le servo et effectue le nettoyage des GPIO.
"""

import time
from gpiozero import DistanceSensor
from moteur import MotorController
from servo_controller import ServoController
import RPi.GPIO as GPIO


class CarController:
    """
    Contrôleur principal de la voiture autonome.
    
    Cette classe gère les capteurs ultrason, le contrôle des moteurs et le pilotage du servo afin d'assurer
    une conduite en avant en évitant les obstacles.
    """

    def __init__(self):
        """
        Initialise les capteurs, le contrôleur de moteurs et le contrôleur du servo ainsi que les paramètres.
        """
        # Seuils de détection
        self.obstacle_threshold = 15          # Seuil latéral (en cm)
        self.front_threshold = self.obstacle_threshold + 15  # Seuil frontal (marge supplémentaire)

        # Angles de virage (en degrés)
        self.angle_virage_gauche = -40          # Virage à gauche (valeur négative)
        self.angle_virage_droite = 40           # Virage à droite (valeur positive)
        self.angle_central = 45                 # Position neutre / point mort

        # Durées (en secondes)
        self.duree_virage = 3                 # Durée d'exécution d'un virage
        self.duree_marche_arriere = 1         # Durée de la marche arrière lors d'un obstacle frontal
        self.reverse_pause = 0.5              # Pause après l'arrêt avant de reculer

        # Initialisation des capteurs ultrason
        self.sensor_left = DistanceSensor(trigger=26, echo=19, max_distance=4)
        self.sensor_right = DistanceSensor(trigger=11, echo=9, max_distance=4)
        self.sensor_front = DistanceSensor(trigger=6, echo=5, max_distance=4)

        # Initialisation des contrôleurs de moteurs et de servo
        self.motor_ctrl = MotorController()
        self.servo_ctrl = ServoController()

    def run(self):
        """
        Lance la boucle principale de contrôle de la voiture.
        
        La voiture avance en ligne droite et surveille en permanence les obstacles.  
        En fonction des mesures des capteurs, elle déclenche les manœuvres d'évitement appropriées.
        """
        print("Démarrage : la voiture avance en ligne droite...")
        self.motor_ctrl.forward(100)
        self.servo_ctrl.setToDegree(self.angle_central)

        try:
            while True:
                # Lecture des distances (conversion en cm)
                distance_front = self.sensor_front.distance * 100
                distance_left = self.sensor_left.distance * 100
                distance_right = self.sensor_right.distance * 100

                # Affichage de la distance frontale en mode debug
                if distance_front > 1:
                    print(f"Distance avant : {round(distance_front, 2)} cm")

                # Détection d'obstacle par le capteur frontal (prioritaire)
                if distance_front < self.front_threshold:
                    self.handle_front_obstacle()
                # Détection simultanée sur les deux côtés
                elif distance_left < self.obstacle_threshold and distance_right < self.obstacle_threshold:
                    self.handle_double_side_obstacle()
                # Détection sur le côté gauche uniquement
                elif distance_left < self.obstacle_threshold:
                    self.handle_left_obstacle()
                # Détection sur le côté droit uniquement
                elif distance_right < self.obstacle_threshold:
                    self.handle_right_obstacle()

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("Ctrl+C détecté : arrêt en cours...")

        finally:
            self.cleanup()

    def handle_front_obstacle(self):
        """
        Gère la manœuvre d'évitement en cas d'obstacle détecté par le capteur frontal.
        
        La voiture s'arrête immédiatement, effectue une courte marche arrière,
        puis choisit la direction (gauche ou droite) offrant le plus de clearance et entame le virage.
        """
        distance_left = self.sensor_left.distance * 100
        distance_right = self.sensor_right.distance * 100

        print(f"Obstacle frontal détecté ({round(self.sensor_front.distance * 100, 2)} cm). Arrêt immédiat.")
        self.motor_ctrl.stop()
        time.sleep(0.5)

        print("Marche arrière suite à l'obstacle frontal...")
        self.motor_ctrl.backward(-100)
        time.sleep(self.duree_marche_arriere)
        self.motor_ctrl.forward(100)

        # Relecture des distances sur les côtés
        distance_left = self.sensor_left.distance * 100
        distance_right = self.sensor_right.distance * 100

        if distance_left > distance_right:
            print(f"Plus de clearance à gauche (gauche : {round(distance_left, 2)} cm, droite : {round(distance_right, 2)} cm). Virage à gauche.")
            self.servo_ctrl.rotate(self.angle_virage_gauche)
        else:
            print(f"Plus de clearance à droite (gauche : {round(distance_left, 2)} cm, droite : {round(distance_right, 2)} cm). Virage à droite.")
            self.servo_ctrl.rotate(self.angle_virage_droite)

        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)

    def handle_double_side_obstacle(self):
        """
        Gère la situation où les deux capteurs latéraux détectent un obstacle.
        
        La voiture recule brièvement, attend qu'au moins un côté soit dégagé,
        puis effectue un virage dans la direction disposant du plus d'espace.
        """
        print(f"Obstacle double détecté (gauche : {round(self.sensor_left.distance * 100, 2)} cm, droite : {round(self.sensor_right.distance * 100, 2)} cm). Marche arrière...")
        self.motor_ctrl.backward(-100)
        time.sleep(self.duree_marche_arriere)
        self.motor_ctrl.forward(100)

        # Attente active jusqu'à ce qu'au moins un côté se libère
        while (self.sensor_left.distance * 100 < self.obstacle_threshold and
               self.sensor_right.distance * 100 < self.obstacle_threshold):
            time.sleep(0.1)

        distance_left = self.sensor_left.distance * 100
        distance_right = self.sensor_right.distance * 100

        if distance_left >= self.obstacle_threshold and distance_right < self.obstacle_threshold:
            print(f"Côté gauche dégagé (gauche : {round(distance_left, 2)} cm). Virage à gauche.")
            self.servo_ctrl.rotate(self.angle_virage_gauche)
        elif distance_right >= self.obstacle_threshold and distance_left < self.obstacle_threshold:
            print(f"Côté droit dégagé (droite : {round(distance_right, 2)} cm). Virage à droite.")
            self.servo_ctrl.rotate(self.angle_virage_droite)
        else:
            if distance_left > distance_right:
                print(f"Les deux côtés dégagés (gauche : {round(distance_left, 2)} cm, droite : {round(distance_right, 2)} cm). Virage à gauche (plus de clearance).")
                self.servo_ctrl.rotate(self.angle_virage_gauche)
            else:
                print(f"Les deux côtés dégagés (gauche : {round(distance_left, 2)} cm, droite : {round(distance_right, 2)} cm). Virage à droite (plus de clearance).")
                self.servo_ctrl.rotate(self.angle_virage_droite)

        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)

    def handle_left_obstacle(self):
        """
        Gère la détection d'un obstacle uniquement sur le côté gauche.
        
        La voiture effectue un virage à gauche.
        """
        print(f"Obstacle détecté par le capteur gauche ({round(self.sensor_left.distance * 100, 2)} cm). Virage à gauche.")
        self.servo_ctrl.rotate(self.angle_virage_gauche)
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)

    def handle_right_obstacle(self):
        """
        Gère la détection d'un obstacle uniquement sur le côté droit.
        
        La voiture effectue un virage à droite.
        """
        print(f"Obstacle détecté par le capteur droit ({round(self.sensor_right.distance * 100, 2)} cm). Virage à droite.")
        self.servo_ctrl.rotate(self.angle_virage_droite)
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)

    def cleanup(self):
        """
        Effectue le nettoyage nécessaire : arrêt des moteurs, désactivation du PWM du servo,
        et nettoyage des broches GPIO.
        """
        self.motor_ctrl.stop()
        self.servo_ctrl.disable_pwm()
        GPIO.cleanup()
        print("Nettoyage des GPIO terminé. La voiture est arrêtée.")


if __name__ == "__main__":
    car_controller = CarController()
    car_controller.run()
