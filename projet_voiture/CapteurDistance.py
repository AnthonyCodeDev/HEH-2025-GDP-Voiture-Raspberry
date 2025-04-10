#!/usr/bin/env python3
"""
CapteurDistance.py
------------------
Ce module gère l'initialisation et la lecture des capteurs de distance utilisés dans le projet voiture.
Il encapsule la configuration et le filtrage des mesures des capteurs ultrason pour les côtés gauche, droit et avant.

Auteur : Vergeylen Anthony
Date   : 08-04-2025
Quoi   : Fournit une classe CapteurDistance pour obtenir les mesures filtrées des capteurs ultrason.
"""

import time

class CapteurDistance:
    """
    Classe de gestion des capteurs de distance ultrason.
    """

    def __init__(self, sensor_left, sensor_right, sensor_front, sensor_sample_count=5, sensor_sample_delay=0.01):
        """
        Initialise les capteurs de distance avec des objets déjà instanciés.

        :param sensor_left: Instance de DistanceSensor pour le capteur gauche.
        :param sensor_right: Instance de DistanceSensor pour le capteur droit.
        :param sensor_front: Instance de DistanceSensor pour le capteur avant.
        :param sensor_sample_count: Nombre d'échantillons à prendre pour filtrer (défaut : 5).
        :param sensor_sample_delay: Délai entre les échantillons en secondes (défaut : 0.01).
        """
        self.sensor_sample_count = sensor_sample_count
        self.sensor_sample_delay = sensor_sample_delay

        self.sensor_left = sensor_left
        self.sensor_right = sensor_right
        self.sensor_front = sensor_front

    def get_filtered_distance(self, sensor):
        """
        Retourne la distance moyenne mesurée par un capteur après filtrage.

        :param sensor: Objet DistanceSensor dont on souhaite obtenir la mesure.
        :return: Distance moyenne en centimètres.
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
        return self.get_filtered_distance(self.sensor_front)
