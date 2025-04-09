#!/usr/bin/env python3
"""
LineFollower.py
---------------
Ce module gère le capteur de suivi de ligne (capteur infrarouge).
Il détecte la présence d'une ligne noire et déclenche l'arrêt de la voiture autonome si nécessaire.

Auteur : Vergeylen Anthony
Date   : 09-04-2025
Quoi   : Fournit une classe LineFollower pour surveiller la ligne et stopper la voiture en cas de détection de ligne noire.
"""

from gpiozero import DigitalInputDevice
from time import sleep
import threading

class LineFollower:
    """
    Classe de gestion du capteur de suivi de ligne.

    QUI : Vergeylen Anthony
    QUOI : Détecte une ligne noire et arrête la voiture si elle est détectée.
    QUAND : 09-04-2025
    """
    def __init__(self, gpio_pin=20):
        self.sensor = DigitalInputDevice(gpio_pin)
        self.monitoring = True

    def monitor(self, car_launcher):
        """
        Lance la surveillance continue du capteur de ligne.
        Si une ligne noire est détectée, la voiture est arrêtée.

        :param car_launcher: Instance de CarLauncher avec méthode shutdown().
        """
        print("🚦 Surveillance de ligne activée...")
        while self.monitoring:
            if not self.sensor.is_active:
                print("⬛ Ligne noire détectée ! Arrêt immédiat de la voiture.")
                car_launcher.shutdown()
                self.monitoring = False
            else:
                print("➡️ Surface claire détectée (blanc)")
            sleep(0.5)

    def stop_monitoring(self):
        self.monitoring = False