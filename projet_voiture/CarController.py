#!/usr/bin/env python3
"""
go.py
------
Ce script commande la voiture pour qu'elle avance en continu et évite les obstacles grâce à trois capteurs ultrason.

Utilisation des capteurs :
    - Capteur gauche (trig 26 / echo 19) : Si la distance est inférieure à 15 cm, considérer obstacle latéral gauche.
    - Capteur droit (trig 11 / echo 9)    : Si la distance est inférieure à 15 cm, considérer obstacle latéral droit.
    - Capteur avant (trig 6 / echo 5)      : Si la distance est inférieure à 30 cm, alors déclencher une manœuvre
      d'évitement, et si la distance descend en dessous de 10 cm, prendre une action d'urgence (arrêt immédiat et marche arrière prolongée).

Après chaque manœuvre, les roues sont ramenées à 45° (point mort).  
En cas d'interruption clavier (Ctrl+C), les moteurs s'arrêtent, le servo est désactivé et les GPIO sont nettoyés.
"""

import time
from gpiozero import DistanceSensor
from MotorController import MotorController
from ServoController import ServoController
import RPi.GPIO as GPIO

class CarController:
    """
    Contrôleur principal pour la voiture autonome.
    
    Cette classe lit et filtre les mesures des capteurs ultrason et commande les moteurs et le servo
    pour assurer une navigation fluide en évitant les obstacles.

    QUI : Vergeylen Anthony
    QUAND : 08-04-2025
    QUOI : Initialise et orchestre la gestion des capteurs, moteurs et servo pour éviter les obstacles.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CarController, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Pour éviter de réinitialiser si l'instance a déjà été initialisée
        if hasattr(self, '_initialized') and self._initialized:
            return

        # Paramètres de détection (en cm)
        self.side_threshold = 15         # Seuil latéral : obstacle sur les côtés
        self.front_threshold = 30        # Seuil frontal : avertissement anticipé
        self.emergency_threshold = 10    # Seuil frontal d'urgence : action immédiate

        # Paramètres de virage et positionnement
        self.angle_virage_gauche = -40   # Virage à gauche
        self.angle_virage_droite = 40    # Virage à droite
        self.angle_central = 45          # Position centrale du servo

        # Durées en secondes
        self.duree_virage = 3
        self.duree_marche_arriere = 1
        self.reverse_pause = 0.5

        # Paramètres du filtrage
        self.sensor_sample_count = 5
        self.sensor_sample_delay = 0.01

        # Initialisation des capteurs ultrason
        self.sensor_left = DistanceSensor(trigger=26, echo=19, max_distance=4)
        self.sensor_right = DistanceSensor(trigger=11, echo=9, max_distance=4)
        self.sensor_front = DistanceSensor(trigger=6, echo=5, max_distance=4)

        # Initialisation des contrôleurs
        self.motor_ctrl = MotorController()
        self.servo_ctrl = ServoController()

        self._initialized = True

    def get_filtered_distance(self, sensor):
        """
        Retourne la distance moyenne mesurée par un capteur après filtrage.

        :param sensor: Instance de DistanceSensor.
        :return: Distance moyenne en cm.

        QUI : Vergeylen Anthony
        QUAND : 08-04-2025
        QUOI : Effectue plusieurs mesures du capteur et retourne la moyenne pour réduire le bruit.
        """
        total = 0.0
        for _ in range(self.sensor_sample_count):
            total += sensor.distance  # gpiozero retourne la distance en mètres
            time.sleep(self.sensor_sample_delay)
        return (total / self.sensor_sample_count) * 100

    def run(self):
        """
        Lance la boucle principale de contrôle de la voiture.

        QUI : Vergeylen Anthony
        QUAND : 08-04-2025
        QUOI : Démarre le mouvement en avant et surveille les capteurs pour déclencher les manœuvres d'évitement.
        """
        print("Démarrage : la voiture avance en ligne droite...")
        self.motor_ctrl.forward(100)
        self.servo_ctrl.setToDegree(self.angle_central)

        try:
            while True:
                # Lire les distances filtrées
                distance_front = self.get_filtered_distance(self.sensor_front)
                distance_left  = self.get_filtered_distance(self.sensor_left)
                distance_right = self.get_filtered_distance(self.sensor_right)

                # Affichage pour le debug
                print(f"Distances -> Avant: {round(distance_front,2)} cm, Gauche: {round(distance_left,2)} cm, Droite: {round(distance_right,2)} cm")

                # Si le capteur frontal détecte un obstacle en dessous du seuil d'urgence
                if distance_front < self.emergency_threshold:
                    print(f"URGENCE! Obstacle frontal très proche ({round(distance_front,2)} cm). Arrêt immédiat.")
                    self.motor_ctrl.stop()
                    time.sleep(0.5)
                    self.motor_ctrl.backward(-100)
                    time.sleep(self.duree_marche_arriere * 1.5)
                    self.motor_ctrl.forward(100)
                    self.servo_ctrl.setToDegree(self.angle_central)

                # Si le capteur frontal détecte un obstacle (mais non en urgence)
                elif distance_front < self.front_threshold:
                    self.handle_front_obstacle()
                # Obstacles détectés simultanément sur les deux côtés
                elif distance_left < self.side_threshold and distance_right < self.side_threshold:
                    self.handle_double_side_obstacle()
                # Obstacle détecté sur le côté gauche
                elif distance_left < self.side_threshold:
                    self.handle_left_obstacle()
                # Obstacle détecté sur le côté droit
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

        La voiture s'arrête, effectue une marche arrière, puis choisit la direction offrant le plus de clearance.

        QUI : Vergeylen Anthony
        QUAND : 08-04-2025
        QUOI : Arrête, recule brièvement et déclenche un virage selon les mesures latérales lors d'un obstacle détecté à l'avant.
        """
        # Récupérer les distances latérales
        distance_left = self.get_filtered_distance(self.sensor_left)
        distance_right = self.get_filtered_distance(self.sensor_right)

        print(f"Obstacle frontal détecté ({round(self.get_filtered_distance(self.sensor_front),2)} cm). Arrêt immédiat.")
        self.motor_ctrl.stop()
        time.sleep(self.reverse_pause)

        print("Marche arrière pour dégager l'obstacle frontal...")
        self.motor_ctrl.backward(-100)
        time.sleep(self.duree_marche_arriere)
        self.motor_ctrl.forward(100)

        # Relecture des distances pour choisir le virage
        distance_left = self.get_filtered_distance(self.sensor_left)
        distance_right = self.get_filtered_distance(self.sensor_right)
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
        Gère la situation où des obstacles sont détectés simultanément sur les deux côtés.

        La voiture recule brièvement, attend qu'au moins un côté se libère, puis effectue le virage le plus approprié.

        QUI : Vergeylen Anthony
        QUAND : 08-04-2025
        QUOI : Réagit quand les obstacles latéraux sont présents des deux côtés en reculant et en choisissant un virage adapté.
        """
        print(f"Obstacle double détecté (Gauche: {round(self.get_filtered_distance(self.sensor_left),2)} cm, Droite: {round(self.get_filtered_distance(self.sensor_right),2)} cm). Marche arrière...")
        self.motor_ctrl.backward(-100)
        time.sleep(self.duree_marche_arriere)
        self.motor_ctrl.forward(100)

        # Attendre que l'un des côtés soit dégagé pour éviter le blocage
        while (self.get_filtered_distance(self.sensor_left) < self.side_threshold and
               self.get_filtered_distance(self.sensor_right) < self.side_threshold):
            time.sleep(0.1)

        distance_left = self.get_filtered_distance(self.sensor_left)
        distance_right = self.get_filtered_distance(self.sensor_right)
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
        Gère l'évitement d'un obstacle détecté sur le côté gauche.

        QUI : Vergeylen Anthony
        QUAND : 08-04-2025
        QUOI : Effectue un virage à gauche en cas de détection d'obstacle latéral gauche.
        """
        print(f"Obstacle détecté sur le côté gauche ({round(self.get_filtered_distance(self.sensor_left),2)} cm). Virage à gauche.")
        self.servo_ctrl.rotate(self.angle_virage_gauche)
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)

    def handle_right_obstacle(self):
        """
        Gère l'évitement d'un obstacle détecté sur le côté droit.

        QUI : Vergeylen Anthony
        QUAND : 08-04-2025
        QUOI : Effectue un virage à droite en cas de détection d'obstacle latéral droit.
        """
        print(f"Obstacle détecté sur le côté droit ({round(self.get_filtered_distance(self.sensor_right),2)} cm). Virage à droite.")
        self.servo_ctrl.rotate(self.angle_virage_droite)
        time.sleep(self.duree_virage)
        self.servo_ctrl.setToDegree(self.angle_central)

    def cleanup(self):
        """
        Arrête les moteurs, désactive le PWM du servo et nettoie les GPIO.

        QUI : Vergeylen Anthony
        QUAND : 08-04-2025
        QUOI : Assure la libération des ressources et un arrêt propre du système.
        """
        self.motor_ctrl.stop()
        self.servo_ctrl.disable_pwm()
        GPIO.cleanup()
        print("Nettoyage des GPIO terminé. La voiture est arrêtée.")


if __name__ == "__main__":
    car_controller = CarController()
    car_controller.run()
