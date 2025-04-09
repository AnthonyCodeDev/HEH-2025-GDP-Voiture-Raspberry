#!/usr/bin/env python3
"""
main.py
-------
Ce script orchestre le lancement du serveur web, du détecteur de couleur RGB (géré par CapteurRGB.py)
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
from LineFollower import LineFollower

class CarLauncher:
    """
    Classe pour lancer le contrôle autonome de la voiture.

    QUI: Vergeylen Anthony
    QUOI: Utilise une instance existante de ControllerCar pour démarrer le contrôle autonome.
    """
    def __init__(self, car_controller):
        self.car_controller = car_controller

    def launch(self):
        self.car_controller.run()

    def shutdown(self):
        print("🔒 Arrêt de la voiture en cours...")
        self.car_controller.cleanup()
        os._exit(0)

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
        # Création d'une seule instance de ControllerCar (Singleton)
        self.car_controller = ControllerCar()
        # Instanciation du capteur RGB depuis le module dédié
        self.rgb_sensor = CapteurRGB(threshold=5, integration_time=100, calibration_duration=5)
        self.car_launcher = CarLauncher(self.car_controller)
        # Transmet l'instance partagée de ControllerCar au serveur web
        self.web_server = VoitureServer(host='0.0.0.0', port=5000, autonomous_controller=self.car_controller, car_launcher=self.car_launcher)

        self.line_follower = LineFollower()

        # Mise en position initiale des roues (45° pour qu'elles soient droites)
        print("🔧 Mise en position initiale des roues (45°).")
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
        print("🌐 Serveur web lancé.")

        # Démarrage de la surveillance RGB dans un thread séparé
        sensor_thread = threading.Thread(target=self.rgb_sensor.monitor, args=(self.car_launcher,))
        sensor_thread.daemon = True
        sensor_thread.start()
        print("🔎 Surveillance RGB lancée.")

        # Démarrage de la surveillance de ligne noire dans un thread séparé
        line_thread = threading.Thread(target=self.line_follower.monitor, args=(self.car_launcher,))
        line_thread.daemon = True
        line_thread.start()
        print("🛣️ Surveillance de ligne lancée.")


        # Boucle principale pour maintenir le programme actif
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("🛑 Arrêt du programme principal.")
            self.shutdown_services()

    def shutdown_services(self):
        print("🔒 Fermeture des services en cours...")
        self.car_launcher.shutdown()
        print("✅ Services fermés proprement.")

if __name__ == '__main__':
    main_controller = MainController()
    main_controller.start_services()
