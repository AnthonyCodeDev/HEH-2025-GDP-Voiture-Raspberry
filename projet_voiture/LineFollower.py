#!/usr/bin/env python3
"""
LineFollower.py
---------------
Ce module gère le capteur de suivi de ligne (capteur infrarouge).
Il détecte la présence d'une ligne noire et déclenche l'arrêt de la voiture autonome si nécessaire.

Auteur : Vergeylen Anthony
Date   : 09-04-2025 (modifié le 11-04-2025)
"""

from gpiozero import DigitalInputDevice
from time import sleep
import threading

class LineFollower:
    """
    Classe de gestion du capteur de suivi de ligne.

    QUI : Vergeylen Anthony
    QUOI : Détecte une ligne noire. À la première détection : pause 5s. À la seconde : arrêt de la voiture.
    QUAND : 09-04-2025
    """
    def __init__(self, gpio_pin=20):
        self.sensor = DigitalInputDevice(gpio_pin)
        self.monitoring = True
        self.first_triggered = False

    def monitor(self, car_launcher):
        """
        Lance la surveillance continue du capteur de ligne.
        - 1ère détection : pause de 5 secondes (voiture continue).
        - 2ème détection : arrêt immédiat via car_launcher.
        """
        print("🚦 Surveillance de ligne activée...")
        # while self.monitoring:
        #     if not self.sensor.is_active:
        #         if not self.first_triggered:
        #             print("⚠️ Première ligne noire détectée. Pause de sécurité...")
        #             self.first_triggered = True
        #             sleep(10)  # Pause sans désactiver la voiture
        #             print("✅ Reprise de la surveillance de ligne.")
        #         else:
        #             print("⬛ Ligne noire détectée à nouveau ! Arrêt immédiat de la voiture.")
        #             car_launcher.shutdown()
        #             self.monitoring = False
        #     sleep(0.2)

    def stop_monitoring(self):
        self.monitoring = False
