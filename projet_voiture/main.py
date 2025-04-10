#!/usr/bin/env python3
"""
main.py
-------
Ce script gère le lancement du serveur web, du détecteur de couleur RGB (géré par CapteurRGB.py)
et du contrôle autonome de la voiture. Chaque fonctionnalité est encapsulée dans une classe dédiée pour
assurer une meilleure modularité et une maintenance facilitée.

QUI: Vergeylen Anthony
QUAND: 09-04-2025
"""

import time
import threading
import os

from ControllerCar import ControllerCar
from WebServerCar import VoitureServer
from CapteurRGB import CapteurRGB
# from LineFollower import LineFollower
from CarLauncher import CarLauncher
from Logging import Logging

class MainController:
    """
    Contrôleur principal orchestrant l'exécution des services:
    - Surveillance du capteur RGB (via CapteurRGB.py).
    - Lancement du contrôle autonome de la voiture.
    - Hébergement du serveur web.

    QUI: Vergeylen Anthony
    QUOI: Initialise et démarre en parallèle l'ensemble des composants du système.
    """
    def __init__(self):

        self.logger = Logging()

        # Création d'une seule instance de ControllerCar (Singleton)
        self.car_controller = ControllerCar()
        self.car_launcher = CarLauncher(self.car_controller)

        self.rgb_sensor = CapteurRGB(threshold=5, integration_time=100, calibration_duration=5)

        self.web_server = VoitureServer(host='0.0.0.0', port=5000, autonomous_controller=self.car_controller, car_launcher=self.car_launcher)

        # self.line_follower = LineFollower()

        self.logger.log("Mise en position initiale des roues (45°).", "lancement_voiture", "INFO")
        self.car_controller.servo_ctrl.setToDegree(self.car_controller.angle_central)
        time.sleep(0.3)
        self.car_controller.servo_ctrl.setToDegree(0)
        time.sleep(0.3)
        self.car_controller.servo_ctrl.setToDegree(self.car_controller.angle_central)
        time.sleep(0.3)
        self.car_controller.servo_ctrl.setToDegree(90)
        time.sleep(0.3)
        self.car_controller.servo_ctrl.setToDegree(self.car_controller.angle_central)
        time.sleep(0.3)
        self.car_controller.servo_ctrl.disable_pwm()

    def start_services(self):
        # Calibration du capteur RGB
        self.rgb_sensor.calibrate()

        # Démarrage du serveur web dans un thread séparé
        server_thread = threading.Thread(target=self.web_server.run)
        server_thread.daemon = True
        server_thread.start()
        self.logger.log("Serveur web lancé.", "lancement_voiture", "INFO")

        # Démarrage de la surveillance RGB dans un thread séparé
        sensor_thread = threading.Thread(target=self.rgb_sensor.monitor, args=(self.car_launcher,))
        sensor_thread.daemon = True
        sensor_thread.start()
        self.logger.log("Surveillance RGB lancée.", "lancement_voiture", "INFO")

        # Démarrage de la surveillance de ligne noire dans un thread séparé
        # line_thread = threading.Thread(target=self.line_follower.monitor, args=(self.car_launcher,))
        # line_thread.daemon = True
        # line_thread.start()
        # print("🛣️ Surveillance de ligne lancée.")


        # Boucle principale pour maintenir le programme actif
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.log("Arrêt du programme principal.", "lancement_voiture", "INFO")
            self.shutdown_services()

    def shutdown_services(self):
        self.logger.log("Arrêt des services en cours...", "lancement_voiture", "INFO")
        self.car_launcher.shutdown()
        self.logger.log("Services fermés proprement.", "lancement_voiture", "INFO")
