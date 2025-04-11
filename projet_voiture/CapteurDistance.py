#!/usr/bin/env python3
"""
CapteurDistance.py
------------------
Ce module gère la lecture d'un capteur de distance (ultrason) pour le projet voiture.
Chaque instance de la classe représente UN capteur.
Le filtrage de la mesure se fait en réalisant plusieurs lectures et en en faisant la moyenne.

Auteur : Vergeylen Anthony
Date   : 08-04-2025
Quoi   : Fournit la classe CapteurDistance pour obtenir une mesure filtrée d'un capteur unique.
"""

import time
from gpiozero import DistanceSensor

VALID_PIN_PAIRS = [
    (11, 9),  # Couple gauche
    (26, 19), # Couple droite
    (6, 5)     # Couple avant
]

class CapteurDistance:
    """
    Classe de gestion d'un capteur de distance ultrason.
    """

    def __init__(self, trigger, echo, max_distance=4, sensor_sample_count=5, sensor_sample_delay=0.01):
        """
        Initialise le capteur de distance.

        :param trigger: Numéro de broche GPIO pour le signal trigger.
        :param echo: Numéro de broche GPIO pour le signal echo.
        :param max_distance: Distance maximale (en mètres) détectable par le capteur (défaut : 4).
        :param sensor_sample_count: Nombre d'échantillons utilisés pour calculer la moyenne (défaut : 5).
        :param sensor_sample_delay: Délai entre chaque lecture (en secondes, défaut : 0.01).
        """
        MAX_SAMPLE_COUNT = 1000
        MAX_SAMPLE_DELAY = 10

        if sensor_sample_count <= 0 or sensor_sample_count > MAX_SAMPLE_COUNT:
            raise ValueError(f"Le nombre d'échantillons doit être compris entre 1 et {MAX_SAMPLE_COUNT}.")
        
        if sensor_sample_delay <= 0 or sensor_sample_delay > MAX_SAMPLE_DELAY:
            raise ValueError(f"Le nombre d'échantillons doit être compris entre 1 et {MAX_SAMPLE_DELAY}.")
        
        if (trigger, echo) not in VALID_PIN_PAIRS:
            raise ValueError(f"Les paires trigger et echo ({trigger}, {echo}) ne sont pas valides.")
        else:
            self.sensor = DistanceSensor(trigger=trigger, echo=echo, max_distance=max_distance)
        
        if sensor_sample_count <= 0:
            raise ValueError("Le nombre d'échantillons doit être supérieur à zéro.")
        if sensor_sample_delay <= 0:
            raise ValueError("Le délai d'échantillonnage doit être supérieur à zéro.")
        if max_distance <= 0:
            raise ValueError("La distance maximale doit être supérieure à zéro.")
    
        self.sensor_sample_count = sensor_sample_count
        self.sensor_sample_delay = sensor_sample_delay

    def get_distance(self):
        """
        Retourne la distance mesurée par le capteur après filtrage (moyenne de plusieurs lectures).

        :return: Distance en centimètres.
        """
        total = 0.0
        try:
            for _ in range(self.sensor_sample_count):
                total += self.sensor.distance  # distance en mètres
                time.sleep(self.sensor_sample_delay)
                distance_total = (total / self.sensor_sample_count) * 100
            if distance_total < 2:
                print("Obstacle trop proche")
                raise ValueError("Distance trop proche")
            if distance_total > 400:
                print("Obstacle trop loin")
                raise ValueError("Distance trop loin")

            return distance_total

        except RuntimeError as e:
            print(f"Erreur capteur : {e}")
            raise RuntimeError(f"Onde pas revenu : {e}")