#!/usr/bin/env python3
"""
LineFollower.py
---------------
Ce module gère le capteur de suivi de ligne (capteur infrarouge).
Il détecte la présence d'une ligne noire et déclenche l'arrêt de la voiture autonome après un nombre défini de détections.

Auteur : Vergeylen Anthony
Date   : 09-04-2025 (modifié le 11-04-2025)
"""

from gpiozero import DigitalInputDevice
from time import sleep
import threading
from Logging import Logging

class LineFollower:
    """
    Classe de gestion du capteur de suivi de ligne.

    QUI : Vergeylen Anthony  
    QUOI : Détecte une ligne noire. À chaque détection : action spécifique. Arrêt après un nombre défini de détections.  
    QUAND : 09-04-2025

    """
    def __init__(self, gpio_pin=20, max_triggers=2):
        """
        Initialise le capteur de ligne avec le GPIO spécifié.

        - :param gpio_pin: Numéro du GPIO utilisé pour le capteur de ligne.
        - :param max_triggers: Nombre maximum de détections avant arrêt de la voiture. (Par exemple si le max_triggers est 2, la voiture s'arrête après 2 détections de ligne noire).

        """
        self.sensor = DigitalInputDevice(gpio_pin)
        self.monitoring = True
        self.trigger_count = 0
        self.max_triggers = max_triggers
        self.last_state = True
        self.logger = Logging()

    def monitor(self, car_launcher):
        """
        Lance la surveillance continue du capteur de ligne.
        - À chaque détection : augmentation du compteur.
        - Si première fois : pause de 5 secondes.
        - Si atteint max_triggers : arrêt immédiat via car_launcher.
        """
        print("🚦 Surveillance de ligne activée...")
        while self.monitoring:
            if not self.sensor.is_active and self.last_state:
                self.trigger_count += 1
                self.logger.log(f"⚠️ Ligne noire détectée ({self.trigger_count}/{self.max_triggers})", "line_follower", "INFO")
                if self.trigger_count == 1:
                    self.logger.log(f"⏸️ Première détection : pause de sécurité...", "line_follower", "INFO")
                    sleep(5)
                    print("✅ Reprise de la surveillance.")
                elif self.trigger_count >= self.max_triggers:
                    self.logger.log("🛑 Arrêt de la voiture après détection de ligne noire.", "line_follower", "INFO")
                    car_launcher.shutdown()
                    self.monitoring = False

                self.last_state = False
            elif self.sensor.is_active:
                self.last_state = True 

            sleep(0.2)

    def stop_monitoring(self):
        self.monitoring = False
