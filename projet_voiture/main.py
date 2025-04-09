#!/usr/bin/env python3
"""
main.py
-------
Ce script orchestre le lancement du serveur web, du détecteur de couleur RGB
et du contrôle autonome de la voiture. Chaque fonctionnalité est encapsulée
dans une classe dédiée pour assurer une meilleure modularité et une maintenance facilitée.

QUI: Vergeylen Anthony
QUAND: 09-04-2025
"""

import time
import threading
import board
import busio
import adafruit_tcs34725

from CarController import CarController
from serveur_voiture import app

class RGBSensorController:
    """
    Classe pour gérer le capteur RGB, effectuer la calibration et surveiller la couleur ambiante.
    
    QUI: Vergeylen Anthony
    QUAND: 09-04-2025
    QUOI: Initialise le capteur RGB, réalise une calibration pour obtenir les valeurs de référence,
          puis détecte en continu la couleur dominante afin de déclencher une action.
    """
    def __init__(self, threshold=5, integration_time=100, calibration_duration=5):
        """
        Initialise le capteur RGB et définit les paramètres de calibration.

        :param threshold: Seuil de variation pour considérer une nouvelle mesure (par défaut 5).
        :param integration_time: Temps d'intégration du capteur en millisecondes (par défaut 100).
        :param calibration_duration: Durée de la phase de calibration en secondes (par défaut 5).

        QUI: Vergeylen Anthony
        QUAND: 09-04-2025
        QUOI: Configure le capteur et initialise les paramètres pour la détection de couleur.
        """
        self.threshold = threshold
        self.integration_time = integration_time
        self.calibration_duration = calibration_duration

        # Initialisation du bus I2C et du capteur RGB
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_tcs34725.TCS34725(self.i2c)
        self.sensor.enable = True
        self.sensor.integration_time = integration_time

        # Variables de calibration
        self.ref_r = None
        self.ref_g = None
        self.ref_b = None

    def calibrate(self):
        """
        Effectue la calibration du capteur RGB pendant une durée spécifiée pour obtenir
        les valeurs de référence (ref_r, ref_g, ref_b).

        QUI: Vergeylen Anthony
        QUAND: 09-04-2025
        QUOI: Calcule les valeurs moyennes RGB sur une période donnée afin d'établir la base de comparaison.
        """
        print("🛠️ Calibration en cours... Ne touchez à rien pendant 5 secondes.")
        nb_mesures = 0
        somme_r = somme_g = somme_b = 0
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
        print(f"✅ Calibration terminée. RGB de base : R={self.ref_r}, G={self.ref_g}, B={self.ref_b}")

    def detect_color(self, r, g, b):
        """
        Détermine la couleur dominante à partir des valeurs RGB mesurées.

        :param r: Valeur du rouge.
        :param g: Valeur du vert.
        :param b: Valeur du bleu.
        :return: Un str indiquant la couleur dominante ("rouge", "vert", "bleu" ou "indéterminé").

        QUI: Vergeylen Anthony
        QUAND: 09-04-2025
        QUOI: Compare les composantes RGB pour identifier laquelle est la plus élevée.
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
        Surveille en continu le capteur RGB et, en cas de détection d'une couleur dominante verte,
        déclenche le lancement du contrôle autonome de la voiture via l'instance fournie.

        :param car_launcher: Instance de CarLauncher permettant de lancer la voiture autonome.

        QUI: Vergeylen Anthony
        QUAND: 09-04-2025
        QUOI: Mesure les valeurs RGB, compare avec la calibration et déclenche le lancement de la voiture
              si la couleur dominante est le vert.
        """
        print("🕵️ Détection des couleurs en cours...")
        car_launched = False
        while True:
            r, g, b = self.sensor.color_rgb_bytes
            ecart_r = abs(r - self.ref_r)
            ecart_g = abs(g - self.ref_g)
            ecart_b = abs(b - self.ref_b)
            if ecart_r > self.threshold or ecart_g > self.threshold or ecart_b > self.threshold:
                couleur = self.detect_color(r, g, b)
                print(f"R: {r}, G: {g}, B: {b} -> Couleur détectée: {couleur}")
                if couleur == "vert" and not car_launched:
                    print("✅ Couleur verte détectée ! Lancement de la voiture autonome.")
                    # Lancer le contrôle de la voiture dans un thread séparé
                    car_thread = threading.Thread(target=car_launcher.launch)
                    car_thread.start()
                    car_launched = True
            time.sleep(1)


class CarLauncher:
    """
    Classe pour lancer le contrôle autonome de la voiture.
    
    QUI: Vergeylen Anthony
    QUAND: 09-04-2025
    QUOI: Instancie et démarre le module de contrôle autonome de la voiture.
    """
    def __init__(self):
        """
        Initialise l'instance de CarController à partir du module go.

        QUI: Vergeylen Anthony
        QUAND: 09-04-2025
        QUOI: Prépare le lancement du contrôle de la voiture autonome.
        """
        self.car_controller = CarController()

    def launch(self):
        """
        Démarre la boucle de contrôle autonome de la voiture en appelant la méthode run() du CarController.

        QUI: Vergeylen Anthony
        QUAND: 09-04-2025
        QUOI: Active le contrôle de la navigation autonome de la voiture.
        """
        self.car_controller.run()

    def shutdown(self):
        """
        Arrête le contrôle autonome de la voiture et réalise les opérations de fermeture (arrêt des moteurs, nettoyage des GPIO, etc.).

        QUI: Vergeylen Anthony
        QUAND: 09-04-2025
        QUOI: Stoppe la voiture, désactive les moteurs et nettoie les ressources pour un arrêt propre.
        """
        print("🔒 Arrêt de la voiture en cours...")
        self.car_controller.cleanup()


class WebServer:
    """
    Classe pour gérer le lancement du serveur web basé sur Flask.
    
    QUI: Vergeylen Anthony
    QUAND: 09-04-2025
    QUOI: Lance l'application Flask pour permettre le contrôle via une interface web.
    """
    def __init__(self, host='0.0.0.0', port=5000):
        """
        Initialise les paramètres d'hébergement du serveur web.

        :param host: Adresse IP à utiliser pour héberger le serveur (par défaut '0.0.0.0').
        :param port: Port à utiliser pour le serveur (par défaut 5000).

        QUI: Vergeylen Anthony
        QUAND: 09-04-2025
        QUOI: Configure l'adresse et le port pour le serveur web.
        """
        self.host = host
        self.port = port

    def run(self):
        """
        Démarre l'application Flask sur le host et le port spécifiés.

        QUI: Vergeylen Anthony
        QUAND: 09-04-2025
        QUOI: Lance le serveur web pour l'accès via le navigateur.
        """
        print(f"🌐 Lancement du serveur web sur {self.host}:{self.port}")
        app.run(host=self.host, port=self.port)


class MainController:
    """
    Contrôleur principal orchestrant l'exécution des services:
    - Détection de couleur via le capteur RGB.
    - Lancement du contrôle autonome de la voiture.
    - Hébergement du serveur web.

    QUI: Vergeylen Anthony
    QUAND: 09-04-2025
    QUOI: Initialise et démarre en parallèle l'ensemble des fonctionnalités de la voiture autonome.
    """
    def __init__(self):
        """
        Initialise les instances des contrôleurs RGB, de la voiture autonome et du serveur web.

        QUI: Vergeylen Anthony
        QUAND: 09-04-2025
        QUOI: Prépare les composants principaux du système pour le démarrage.
        """
        self.rgb_sensor = RGBSensorController(threshold=5, integration_time=100, calibration_duration=5)
        self.car_launcher = CarLauncher()
        self.web_server = WebServer(host='0.0.0.0', port=5000)

    def start_services(self):
        """
        Démarre l'ensemble des services en les exécutant dans des threads séparés :
        - Calibration du capteur RGB.
        - Lancement du serveur web Flask.
        - Surveillance en continu du capteur RGB pour déclencher la voiture autonome en cas de détection de vert.
        
        La méthode reste active jusqu'à une interruption clavier (CTRL+C), à partir de laquelle elle
        déclenche la fermeture propre des services.

        QUI: Vergeylen Anthony
        QUAND: 09-04-2025
        QUOI: Orchestre et démarre les différents composants du système de contrôle de la voiture.
        """
        # Calibration du capteur RGB
        self.rgb_sensor.calibrate()

        # Lancer le serveur web dans un thread séparé
        server_thread = threading.Thread(target=self.web_server.run)
        server_thread.daemon = True  # Ce thread se termine avec le programme principal
        server_thread.start()
        print("🌐 Serveur web lancé.")

        # Lancer la surveillance du capteur RGB dans un thread séparé
        sensor_thread = threading.Thread(target=self.rgb_sensor.monitor, args=(self.car_launcher,))
        sensor_thread.daemon = True
        sensor_thread.start()
        print("🔎 Détecteur RGB lancé.")

        # Boucle principale pour maintenir le programme actif et attendre une interruption
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("🛑 Arrêt du programme principal.")
            self.shutdown_services()

    def shutdown_services(self):
        """
        Arrête et nettoie proprement tous les services en cours d'exécution, incluant
        l'arrêt de la voiture autonome.

        QUI: Vergeylen Anthony
        QUAND: 09-04-2025
        QUOI: Appelle les procédures de fermeture pour arrêter la voiture et nettoyer les ressources.
        """
        print("🔒 Fermeture des services en cours...")
        self.car_launcher.shutdown()
        print("✅ Services fermés proprement.")


if __name__ == '__main__':
    main_controller = MainController()
    main_controller.start_services()
