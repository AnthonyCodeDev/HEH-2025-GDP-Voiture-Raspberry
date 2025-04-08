#!/usr/bin/env python3
"""
tour_en_8.py
-------------
Fait réaliser à la voiture un trajet en forme de « 8 » puis arrête la voiture.

Auteur : Anthony Vergeylen
Date   : 08-04-2025
Quoi   : Combinaison de commandes moteurs et servo pour tracer un chemin en 8.
"""

import time
import RPi.GPIO as GPIO
from moteur import MotorController
from servo_controller import ServoController

def tour_en_8():
    """
    Exécute la séquence pour réaliser un tour en 8.

    La séquence effectuée est la suivante :
      1. On démarre en avançant tout en dirigeant les roues vers la droite (virage droit).
      2. Ensuite, on inverse le virage pour diriger les roues vers la gauche, formant ainsi le grand arc du 8.
      3. Puis, on recompose un virage vers la droite pour compléter la figure en 8.
      4. Enfin, on arrête les moteurs et on remet les roues en position droite (centrée).

    Les temps de pause (time.sleep) sont donnés à titre indicatif et devront être ajustés
    en fonction de la vitesse réelle du véhicule et de la courbure souhaitée.
    """
    # Instanciation des contrôleurs
    motor = MotorController()
    servo = ServoController()

    try:
        print("Début du tour en 8")

        # 1. Premier arc : courbe vers la droite
        # La commande rotate avec une valeur positive (ici 50) oriente les roues vers la droite.
        servo.rotate(50)
        motor.forward(80)  # La vitesse est ici fixée à 80 (sur une échelle de 0 à 100)
        time.sleep(3)      # Durée approximative pour réaliser le premier arc
        
        # 2. Deuxième arc : inversion du virage vers la gauche
        # En passant la valeur -50, on fait pivoter les roues vers la gauche.
        servo.rotate(-50)
        time.sleep(6)      # Durée approximative pour former le grand arc du 8
        
        # 3. Troisième arc : retour à un virage vers la droite
        servo.rotate(50)
        time.sleep(3)      # Complétion du mouvement en 8

        # 4. Arrêt de la voiture et remise des roues en position droite
        print("Fin du tour en 8 - Arrêt de la voiture")
        motor.stop()
        servo.resetRoue()

    except Exception as e:
        print("Erreur lors de l'exécution du tour en 8 :", e)
    finally:
        # Nettoyage des ressources GPIO, indispensable pour éviter les conflits lors de
        # prochaines utilisations du matériel.
        GPIO.cleanup()
        print("Nettoyage des GPIO terminé.")

if __name__ == "__main__":
    tour_en_8()
