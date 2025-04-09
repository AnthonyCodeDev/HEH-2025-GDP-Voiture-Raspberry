#!/usr/bin/env python3
"""
CapteurDistance.py
------------------
Ce module gère l'initialisation et la lecture des capteurs de distance utilisés dans le projet voiture.
Il encapsule la configuration et le filtrage des mesures des capteurs ultrason pour les côtés gauche, droit et avant.

Auteur : Vergeylen Anthony
Date   : 08-04-2025
Quoi   : Fournit une classe CapteurDistance pour initialiser et obtenir les distances mesurées par les capteurs ultrason.
"""

import time
from gpiozero import DistanceSensor

class CapteurDistance:
    """
    Classe de gestion des capteurs de distance ultrason.

    QUI: Vergeylen Anthony
    QUAND: 08-04-2025
    QUOI: Initialise les capteurs (gauche, droit et avant) et fournit des méthodes pour obtenir des mesures filtrées.
    """
    def __init__(self, sensor_sample_count=5, sensor_sample_delay=0.01, max_distance=4):
        """
        Initialise les capteurs de distance.

        :param sensor_sample_count: Nombre d'échantillons à prendre pour le filtrage (par défaut 5).
        :param sensor_sample_delay: Délai entre chaque lecture en secondes (par défaut 0.01).
        :param max_distance: Distance maximale en mètres détectable par les capteurs (par défaut 4).

        QUI: Vergeylen Anthony
        QUAND: 08-04-2025
        QUOI: Configure et initialise les objets DistanceSensor pour les capteurs gauche, droit et avant.
        """
        self.sensor_sample_count = sensor_sample_count
        self.sensor_sample_delay = sensor_sample_delay

        self.sensor_left = DistanceSensor(trigger=26, echo=19, max_distance=max_distance)
        self.sensor_right = DistanceSensor(trigger=11, echo=9, max_distance=max_distance)
        self.sensor_front = DistanceSensor(trigger=6, echo=5, max_distance=max_distance)

    def get_filtered_distance(self, sensor):
        """
        Retourne la distance moyenne mesurée par un capteur après application d'un filtrage.

        :param sensor: Instance de DistanceSensor dont on souhaite obtenir la mesure.
        :return: Distance moyenne en centimètres.

        QUI: Vergeylen Anthony
        QUAND: 08-04-2025
        QUOI: Calcule la moyenne de plusieurs lectures pour réduire le bruit dans la mesure.
        """
        total = 0.0
        for _ in range(self.sensor_sample_count):
            total += sensor.distance  # distance en mètres
            time.sleep(self.sensor_sample_delay)
        return (total / self.sensor_sample_count) * 100

    def get_distance_left(self):
        """
        Retourne la distance filtrée mesurée par le capteur gauche.

        :return: Distance en centimètres.
        """
        return self.get_filtered_distance(self.sensor_left)

    def get_distance_right(self):
        """
        Retourne la distance filtrée mesurée par le capteur droit.

        :return: Distance en centimètres.
        """
        return self.get_filtered_distance(self.sensor_right)

    def get_distance_front(self):
        """
        Retourne la distance filtrée mesurée par le capteur avant.

        :return: Distance en centimètres.
        """
        print("Distance avant : ", self.sensor_front.distance)
        return self.get_filtered_distance(self.sensor_front)
