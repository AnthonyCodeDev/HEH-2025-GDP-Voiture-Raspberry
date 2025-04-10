#!/usr/bin/env python3
"""
CapteurRGB.py
-------------
Ce module gère l'initialisation et la lecture du capteur de couleur RGB.
Il permet de calibrer le capteur pour établir une référence et fournit des méthodes 
pour détecter la couleur dominante.

Auteur : Vergeylen Anthony
Date   : 09-04-2025
Quoi   : Gère le capteur RGB (via adafruit_tcs34725) et fournit des méthodes pour la calibration 
         et la détection de couleur.
Vérfié : Matteo Di Leto
"""

import time
import board
import busio
import adafruit_tcs34725
import threading

class CapteurRGB:
    def __init__(self, threshold=5, integration_time=100, calibration_duration=5):
        """
        Initialise le capteur RGB et configure les paramètres de calibration.

        :param threshold: Seuil de variation pour déclencher une détection (par défaut 5).
        :param integration_time: Temps d'intégration du capteur en millisecondes (par défaut 100).
        :param calibration_duration: Durée de la calibration en secondes (par défaut 5).

        """
        self.threshold = threshold
        self.integration_time = integration_time
        self.calibration_duration = calibration_duration

        # Initialisation du bus I²C et du capteur RGB
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_tcs34725.TCS34725(self.i2c)
        self.sensor.enable = True
        self.sensor.integration_time = integration_time

        self.ref_r = None
        self.ref_g = None
        self.ref_b = None

    def calibrate(self):
        #Effectue la calibration du capteur RGB pour établir une référence de couleur.
        
        print("Calibration RGB en cours... Ne touchez à rien pendant 5 secondes.")
        nb_mesures = 0
        somme_r, somme_g, somme_b = 0, 0, 0
        debut = time.time()
        while time.time() - debut < self.calibration_duration:
            r, g, b = self.sensor.color_rgb_bytes
            somme_r += r
            somme_g += g
            somme_b += b
            nb_mesures += 1
            time.sleep(0.1)
        self.ref_r = somme_r // nb_mesures
        self.ref_g = somme_g // nb_mesures
        self.ref_b = somme_b // nb_mesures
        print(f"Calibration RGB terminée. Référence: R={self.ref_r}, G={self.ref_g}, B={self.ref_b}")

    def detect_color(self, r, g, b):
        """
        Détermine la couleur dominante à partir des valeurs RGB mesurées.

        :param r: Valeur du rouge.
        :param g: Valeur du vert.
        :param b: Valeur du bleu.
        :return: La couleur dominante ("rouge", "vert", "bleu" ou "indéterminé")
        """
        if r > g and r > b:
            return "rouge"
        elif g > r and g > b:
            return "vert"
        elif b > r and b > g:
            return "bleu"
        else:
            return "indéterminé"

    def monitor(self, car_launcher):
        """
        Surveille continuellement le capteur RGB et déclenche le lancement de la voiture autonome
        si la couleur dominante détectée est "vert".

        :param car_launcher: Instance de CarLauncher qui permet de lancer le contrôle autonome.
        """
        print("Surveillance RGB en cours...")
        car_launched = False
        while True:
            r, g, b = self.sensor.color_rgb_bytes
            diff_r = abs(r - self.ref_r)
            diff_g = abs(g - self.ref_g)
            diff_b = abs(b - self.ref_b)
            if diff_r > self.threshold or diff_g > self.threshold or diff_b > self.threshold:
                couleur = self.detect_color(r, g, b)
                print(f"RGB: R={r}, G={g}, B={b} -> Couleur détectée: {couleur}")
                if couleur == "vert" and not car_launched:
                    print("Couleur verte détectée ! Lancement de la voiture autonome.")
                    thread = threading.Thread(target=car_launcher.launch)
                    thread.start()
                    car_launched = True
            time.sleep(1)
