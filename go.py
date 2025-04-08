#!/usr/bin/env python3
"""
go.py
------
Ce script commande la voiture pour qu'elle avance indéfiniment. Deux capteurs ultrason
sont surveillés pour détecter les obstacles :
    - Le capteur sur trig 26 / echo 19 : si la distance est inférieure à 15 cm, tourner à gauche.
    - Le capteur sur trig 11 / echo 9   : si la distance est inférieure à 15 cm, tourner à droite.
Si les deux capteurs détectent un obstacle simultanément (distance < 15 cm), la voiture recule
un instant, puis attend qu'un côté soit dégagé pour tourner dans cette direction et reprendre la marche avant.
Après chaque action d'évitement, les roues sont remises à 45° (point mort).
Lors de l'appui sur Ctrl+C, le script arrête proprement les moteurs, désactive le servo et réalise le nettoyage des GPIO.
"""

import time
from gpiozero import DistanceSensor
from moteur import MotorController
from servo_controller import ServoController
import RPi.GPIO as GPIO  # Pour le nettoyage des GPIO

# Seuil de distance (en cm) pour déclencher l'évitement d'obstacle
OBSTACLE_THRESHOLD_CM = 15

# Angle de virage relatif pour l'évitement (ajustable)
ANGLE_VIRAGE_GAUCHE = -40  # un angle négatif tourne vers la gauche
ANGLE_VIRAGE_DROITE = 40   # un angle positif tourne vers la droite

# Durée du virage (en secondes)
DUREE_VIRAGE = 3

# Durée de marche arrière lors d'un obstacle double (en secondes)
DUREE_MARCHE_ARRIERE = 1

# Angle central (point mort) exprimé en degrés pour le servo
ANGLE_CENTRAL = 45

def main():
    print("Initialisation des capteurs et des contrôleurs...")
    # Initialisation du capteur gauche (Trig 26, Echo 19)
    capteur_gauche = DistanceSensor(trigger=26, echo=19, max_distance=4)
    # Initialisation du capteur droit (Trig 11, Echo 9)
    capteur_droite = DistanceSensor(trigger=11, echo=9, max_distance=4)
    
    # Initialisation des contrôleurs de moteurs et du servo pour la direction
    motor_ctrl = MotorController()
    servo_ctrl = ServoController()
    
    # Démarrage : la voiture avance en ligne droite avec les roues au point mort (45°)
    print("Démarrage : la voiture avance en ligne droite...")
    motor_ctrl.forward(100)
    servo_ctrl.setToDegree(ANGLE_CENTRAL)
    
    try:
        while True:
            # Lecture des distances (conversion en cm)
            distance_gauche = capteur_gauche.distance * 100
            distance_droite = capteur_droite.distance * 100
            
            # Cas où les deux capteurs détectent un obstacle en même temps
            if distance_gauche < OBSTACLE_THRESHOLD_CM and distance_droite < OBSTACLE_THRESHOLD_CM:
                print(f"Obstacle double détecté (gauche: {round(distance_gauche,2)} cm, droite: {round(distance_droite,2)} cm). Recule...")
                # Marche arrière pour dégager la voiture
                motor_ctrl.backward(-100)
                time.sleep(DUREE_MARCHE_ARRIERE)
                # Reprendre ensuite la marche avant
                motor_ctrl.forward(100)
                
                # Attente active jusqu'à ce qu'au moins un côté soit dégagé
                while (capteur_gauche.distance * 100 < OBSTACLE_THRESHOLD_CM and
                       capteur_droite.distance * 100 < OBSTACLE_THRESHOLD_CM):
                    time.sleep(0.1)
                
                # Mise à jour des distances
                distance_gauche = capteur_gauche.distance * 100
                distance_droite = capteur_droite.distance * 100
                
                # Choix du virage en fonction du côté dégagé
                if distance_gauche >= OBSTACLE_THRESHOLD_CM and distance_droite < OBSTACLE_THRESHOLD_CM:
                    print(f"Côté gauche dégagé (gauche: {round(distance_gauche,2)} cm). Virage à gauche.")
                    servo_ctrl.rotate(ANGLE_VIRAGE_GAUCHE)
                    time.sleep(DUREE_VIRAGE)
                    servo_ctrl.setToDegree(ANGLE_CENTRAL)
                elif distance_droite >= OBSTACLE_THRESHOLD_CM and distance_gauche < OBSTACLE_THRESHOLD_CM:
                    print(f"Côté droit dégagé (droite: {round(distance_droite,2)} cm). Virage à droite.")
                    servo_ctrl.rotate(ANGLE_VIRAGE_DROITE)
                    time.sleep(DUREE_VIRAGE)
                    servo_ctrl.setToDegree(ANGLE_CENTRAL)
                else:
                    # Si les deux côtés sont dégagés, tourner dans la direction offrant plus de clearance
                    if distance_gauche > distance_droite:
                        print(f"Les deux côtés dégagés (gauche: {round(distance_gauche,2)} cm, droite: {round(distance_droite,2)} cm). Virage à gauche (plus de clearance).")
                        servo_ctrl.rotate(ANGLE_VIRAGE_GAUCHE)
                        time.sleep(DUREE_VIRAGE)
                        servo_ctrl.setToDegree(ANGLE_CENTRAL)
                    else:
                        print(f"Les deux côtés dégagés (gauche: {round(distance_gauche,2)} cm, droite: {round(distance_droite,2)} cm). Virage à droite (plus de clearance).")
                        servo_ctrl.rotate(ANGLE_VIRAGE_DROITE)
                        time.sleep(DUREE_VIRAGE)
                        servo_ctrl.setToDegree(ANGLE_CENTRAL)
            
            # Si seul le capteur gauche détecte un obstacle
            elif distance_gauche < OBSTACLE_THRESHOLD_CM:
                print(f"Obstacle détecté par le capteur gauche ({round(distance_gauche,2)} cm). Virage à gauche.")
                servo_ctrl.rotate(ANGLE_VIRAGE_GAUCHE)
                time.sleep(DUREE_VIRAGE)
                servo_ctrl.setToDegree(ANGLE_CENTRAL)
            
            # Si seul le capteur droit détecte un obstacle
            elif distance_droite < OBSTACLE_THRESHOLD_CM:
                print(f"Obstacle détecté par le capteur droit ({round(distance_droite,2)} cm). Virage à droite.")
                servo_ctrl.rotate(ANGLE_VIRAGE_DROITE)
                time.sleep(DUREE_VIRAGE)
                servo_ctrl.setToDegree(ANGLE_CENTRAL)
            
            # Petite pause pour limiter la fréquence de contrôle
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("Ctrl+C détecté : arrêt en cours...")
    
    finally:
        # Arrêter les moteurs (mise à 0) pour éviter de forcer le matériel
        motor_ctrl.stop()
        # Désactiver la PWM pour libérer le servo
        servo_ctrl.disable_pwm()
        # Nettoyage des GPIO
        GPIO.cleanup()
        print("Nettoyage des GPIO terminé. La voiture est arrêtée.")

if __name__ == "__main__":
    main()
