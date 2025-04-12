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
import threading
from gpiozero import DistanceSensor

class CapteurDistance:
    """
    Classe de gestion d'un capteur de distance ultrason.
    """

    def __init__(self, trigger, echo, max_distance=4, sensor_sample_count=5, sensor_sample_delay=0.01):
        """
        Initialise le capteur de distance.

        :param trigger: Numéro de broche GPIO pour le signal trigger.
        :param echo: Numéro de broche GPIO pour le signal echo.
        :param max_distance: Distance maximale (en mètres) détectable par le capteur (défaut  4).
        :param sensor_sample_count: Nombre d'échantillons utilisés pour calculer la moyenne (défaut  5).
        :param sensor_sample_delay: Délai entre chaque lecture (en secondes, défaut  0.01).
        """
        self.sensor_sample_count = sensor_sample_count
        self.sensor_sample_delay = sensor_sample_delay

        self._stop_event = threading.Event()
        self._thread = None

        self.sensor = DistanceSensor(trigger=trigger, echo=echo, max_distance=max_distance)

    def get_distance(self):
        """
        Retourne la distance mesurée par le capteur après filtrage (moyenne de plusieurs lectures).

        :return: Distance en centimètres.
        """
        total = 0.0
        for _ in range(self.sensor_sample_count):
            total += self.sensor.distance   # distance en mètres
            time.sleep(self.sensor_sample_delay)
        return (total / self.sensor_sample_count) * 100

# Normally all sensors must implement these function but let's just assure CapteurDistance have them at least    
    def start_thread(self):
        """Create and start the sensor update thread"""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self.get_distance, daemon=True)
        self._thread.start()
        print(f"thread commence")

    def stop_thread(self):
        """Signal the thread to stop and wait for it to finish"""
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        print(f"thread terminé")
