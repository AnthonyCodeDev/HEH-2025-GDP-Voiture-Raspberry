#!/usr/bin/env python3
"""
go.py
------
Ce script commande la voiture pour qu'elle avance indéfiniment. Trois capteurs ultrason
sont surveillés pour détecter les obstacles :
    - Capteur gauche (trig 26 / echo 19) : si la distance est inférieure à 15 cm, tourner à gauche.
    - Capteur droit (trig 11 / echo 9)    : si la distance est inférieure à 15 cm, tourner à droite.
    - Capteur avant (trig 6 / echo 5)     : si la distance est inférieure à 15 cm, arrêter, reculer,
      choisir la direction offrant le plus de clearance et repartir.
Après chaque action d'évitement, les roues sont remises à 45° (point mort).
Lors de l'appui sur Ctrl+C, le script arrête proprement les moteurs, désactive le servo
et réalise le nettoyage des GPIO.
"""

import time
from gpiozero import DistanceSensor
from moteur import MotorController
from servo_controller import ServoController
import RPi.GPIO as GPIO  # Pour le nettoyage des GPIO

# Seuil de distance en cm pour déclencher l'évitement d'obstacle
OBSTACLE_THRESHOLD_CM = 15

# Angles de virage relatif (ajustable)
ANGLE_VIRAGE_GAUCHE = -40  # Un angle négatif tourne vers la gauche
ANGLE_VIRAGE_DROITE = 40   # Un angle positif tourne vers la droite

# Durées en secondes
DUREE_VIRAGE = 3              # Durée du virage
DUREE_MARCHE_ARRIERE = 1      # Durée de marche arrière lors de l'obstacle frontal

# Angle central (point mort) en degrés pour le servo
ANGLE_CENTRAL = 45

def main():
    print("Initialisation des capteurs et des contrôleurs...")

    # Initialisation des capteurs :
    capteur_gauche = DistanceSensor(trigger=26, echo=19, max_distance=4)
    capteur_droite = DistanceSensor(trigger=11, echo=9, max_distance=4)
    capteur_avant = DistanceSensor(trigger=6, echo=5, max_distance=4)
    
    # Initialisation des contrôleurs de moteurs et du servo de direction
    motor_ctrl = MotorController()
    servo_ctrl = ServoController()
    
    # Démarrage : avancer en ligne droite avec les roues en position centrale (45°)
    print("Démarrage : la voiture avance en ligne droite...")
    motor_ctrl.forward(100)
    servo_ctrl.setToDegree(ANGLE_CENTRAL)
    
    try:
        while True:
            # Lecture des distances (conversion en cm)
            distance_avant   = capteur_avant.distance * 100
            distance_gauche  = capteur_gauche.distance * 100
            distance_droite  = capteur_droite.distance * 100

            # Priorité au capteur avant
            if distance_avant < OBSTACLE_THRESHOLD_CM:
                print(f"Obstacle détecté par le capteur avant ({round(distance_avant,2)} cm).")
                # Arrêt immédiat
                motor_ctrl.stop()
                time.sleep(0.5)
                # Marche arrière pour se dégager
                print("Marche arrière suite à l'obstacle frontal...")
                motor_ctrl.backward(-100)
                time.sleep(DUREE_MARCHE_ARRIERE)
                motor_ctrl.forward(100)
                
                # Relecture pour choisir la direction la plus dégagée
                distance_gauche = capteur_gauche.distance * 100
                distance_droite = capteur_droite.distance * 100
                
                if distance_gauche > distance_droite:
                    print(f"Plus de clearance à gauche (gauche : {round(distance_gauche,2)} cm, droite : {round(distance_droite,2)} cm). Virage à gauche.")
                    servo_ctrl.rotate(ANGLE_VIRAGE_GAUCHE)
                else:
                    print(f"Plus de clearance à droite (gauche : {round(distance_gauche,2)} cm, droite : {round(distance_droite,2)} cm). Virage à droite.")
                    servo_ctrl.rotate(ANGLE_VIRAGE_DROITE)
                time.sleep(DUREE_VIRAGE)
                servo_ctrl.setToDegree(ANGLE_CENTRAL)
            
            # Gestion de la détection simultanée sur les côtés gauche et droit
            elif distance_gauche < OBSTACLE_THRESHOLD_CM and distance_droite < OBSTACLE_THRESHOLD_CM:
                print(f"Obstacle double détecté (gauche : {round(distance_gauche,2)} cm, droite : {round(distance_droite,2)} cm). Recule...")
                motor_ctrl.backward(-100)
                time.sleep(DUREE_MARCHE_ARRIERE)
                motor_ctrl.forward(100)
                # Attente active jusqu'à ce qu'au moins un côté soit dégagé
                while (capteur_gauche.distance * 100 < OBSTACLE_THRESHOLD_CM and
                       capteur_droite.distance * 100 < OBSTACLE_THRESHOLD_CM):
                    time.sleep(0.1)
                distance_gauche = capteur_gauche.distance * 100
                distance_droite = capteur_droite.distance * 100
                if distance_gauche >= OBSTACLE_THRESHOLD_CM and distance_droite < OBSTACLE_THRESHOLD_CM:
                    print(f"Côté gauche dégagé (gauche : {round(distance_gauche,2)} cm). Virage à gauche.")
                    servo_ctrl.rotate(ANGLE_VIRAGE_GAUCHE)
                elif distance_droite >= OBSTACLE_THRESHOLD_CM and distance_gauche < OBSTACLE_THRESHOLD_CM:
                    print(f"Côté droit dégagé (droite : {round(distance_droite,2)} cm). Virage à droite.")
                    servo_ctrl.rotate(ANGLE_VIRAGE_DROITE)
                else:
                    if distance_gauche > distance_droite:
                        print(f"Les deux côtés dégagés (gauche : {round(distance_gauche,2)} cm, droite : {round(distance_droite,2)} cm). Virage à gauche (plus de clearance).")
                        servo_ctrl.rotate(ANGLE_VIRAGE_GAUCHE)
                    else:
                        print(f"Les deux côtés dégagés (gauche : {round(distance_gauche,2)} cm, droite : {round(distance_droite,2)} cm). Virage à droite (plus de clearance).")
                        servo_ctrl.rotate(ANGLE_VIRAGE_DROITE)
                time.sleep(DUREE_VIRAGE)
                servo_ctrl.setToDegree(ANGLE_CENTRAL)
            
            # Cas obstacle sur le côté gauche uniquement
            elif distance_gauche < OBSTACLE_THRESHOLD_CM:
                print(f"Obstacle détecté par le capteur gauche ({round(distance_gauche,2)} cm). Virage à gauche.")
                servo_ctrl.rotate(ANGLE_VIRAGE_GAUCHE)
                time.sleep(DUREE_VIRAGE)
                servo_ctrl.setToDegree(ANGLE_CENTRAL)
            
            # Cas obstacle sur le côté droit uniquement
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
        # Arrêt des moteurs pour éviter de forcer le matériel
        motor_ctrl.stop()
        # Désactivation de la PWM pour libérer le servo
        servo_ctrl.disable_pwm()
        # Nettoyage des GPIO
        GPIO.cleanup()
        print("Nettoyage des GPIO terminé. La voiture est arrêtée.")

if __name__ == "__main__":
    main()
