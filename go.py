#!/usr/bin/env python3
"""
go.py
------
Ce script commande la voiture pour qu'elle avance indéfiniment. Deux capteurs ultrason
sont surveillés pour détecter les obstacles :
    - Le capteur sur trig 26 / echo 19 : si la distance est inférieure à 15 cm, tourner à gauche.
    - Le capteur sur trig 11 / echo 9   : si la distance est inférieure à 15 cm, tourner à droite.
Après chaque action d'évitement (durée de 3 secondes), les roues sont remises en ligne droite.
"""

import time
from gpiozero import DistanceSensor
from moteur import MotorController
from servo_controller import ServoController

# Seuil de distance en centimètres pour déclencher l'évitement d'obstacle
OBSTACLE_THRESHOLD_CM = 15

# Angle de virage relatif pour l'évitement (ajustable)
ANGLE_VIRAGE_GAUCHE = -40  # un angle négatif tourne vers la gauche
ANGLE_VIRAGE_DROITE = 40   # un angle positif tourne vers la droite

# Durée du virage en secondes
DUREE_VIRAGE = 3

def main():
    print("Initialisation des capteurs et des contrôleurs...")
    # Initialisation du capteur de gauche (Trig 26, Echo 19)
    capteur_gauche = DistanceSensor(trigger=26, echo=19, max_distance=4)
    # Initialisation du capteur de droite (Trig 11, Echo 9)
    capteur_droite = DistanceSensor(trigger=11, echo=9, max_distance=4)
    
    # Initialisation du contrôleur de moteurs et du servo pour la direction
    motor_ctrl = MotorController()
    servo_ctrl = ServoController()
    
    # Démarrage en mouvement vers l'avant et remise à la position droite
    print("Démarrage : la voiture avance en ligne droite...")
    motor_ctrl.forward(100)
    servo_ctrl.resetRoue()  # positionne les roues au centre
    
    try:
        while True:
            # Lecture des distances mesurées (conversion en cm)
            distance_gauche = capteur_gauche.distance * 100
            distance_droite = capteur_droite.distance * 100
            
            # Vérification du capteur gauche pour un obstacle trop proche
            if distance_gauche < OBSTACLE_THRESHOLD_CM:
                print(f"Obstacle détecté par le capteur gauche ({round(distance_gauche,2)} cm). Action : virage à gauche.")
                # Tourner à gauche
                servo_ctrl.rotate(ANGLE_VIRAGE_GAUCHE)
                # On attend pendant la durée du virage
                time.sleep(DUREE_VIRAGE)
                # Remise des roues en position droite
                servo_ctrl.resetRoue()
                print("Virage à gauche terminé, reprise de la trajectoire.")
            
            # Vérification du capteur droite pour un obstacle trop proche
            elif distance_droite < OBSTACLE_THRESHOLD_CM:
                print(f"Obstacle détecté par le capteur droite ({round(distance_droite,2)} cm). Action : virage à droite.")
                # Tourner à droite
                servo_ctrl.rotate(ANGLE_VIRAGE_DROITE)
                time.sleep(DUREE_VIRAGE)
                servo_ctrl.resetRoue()
                print("Virage à droite terminé, reprise de la trajectoire.")
            
            # Petite pause pour éviter de surcharger la boucle de contrôle
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("Arrêt du programme par l'utilisateur.")
    
    finally:
        motor_ctrl.stop()
        print("La voiture est arrêtée.")

if __name__ == "__main__":
    main()
