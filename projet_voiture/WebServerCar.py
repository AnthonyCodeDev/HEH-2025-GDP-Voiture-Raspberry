#!/usr/bin/env python3
"""
WebServerCar.py
--------------------
Ce module fournit une interface web via Flask pour contrôler la voiture.
Les actions possibles incluent :
  - 'lancer'  : Lancer la voiture en mode autonome via ControllerCar.
  - 'avancer' : Faire avancer la voiture en mode simple via VoitureController.
  - 'reset'   : (Non implémenté pour l'instant)
  
De plus, une API est fournie pour obtenir dynamiquement les mesures des capteurs de distance.

Auteur : Anthony Vergeylen
Date   : 08-04-2025
Quoi   : Permet de contrôler la voiture via une interface web et d'accéder aux mesures des capteurs.
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
import threading
import time
from ControllerMotor import ControllerMotor  # Module personnalisé pour contrôler les moteurs
import RPi.GPIO as GPIO
from ControllerCar import ControllerCar     # Module de contrôle autonome de la voiture

class VoitureController:
    """
    Classe pour contrôler la voiture en mode basique.
    
    QUI: Anthony Vergeylen
    QUOI: Fournit une méthode pour faire avancer la voiture en ligne droite.
    """
    def __init__(self, duration=10, speed=100):
        self.duration = duration
        self.speed = speed
        self.motor = ControllerMotor()

    def lancer_voiture(self):
        try:
            print("🚀 Lancement de la voiture en mode avance (simple)...")
            self.motor.forward(self.speed)
            time.sleep(self.duration)
            print("🛑 Arrêt de la voiture")
            self.motor.stop()
        except Exception as e:
            print("Erreur lors du lancement de la voiture (mode avance):", e)
        finally:
            GPIO.cleanup()
            print("Nettoyage des GPIO terminé.")

class VoitureServer:
    """
    Classe pour gérer le serveur web de contrôle de la voiture.

    QUI: Anthony Vergeylen
    QUOI: Permet d'interagir avec la voiture via une interface web ainsi que d'obtenir les mesures des capteurs.
    """
    def __init__(self, host='0.0.0.0', port=5000, autonomous_controller=None):
        self.host = host
        self.port = port
        self.app = Flask(__name__, template_folder='templates')
        if autonomous_controller is None:
            self.autonomous_controller = ControllerCar()
        else:
            self.autonomous_controller = autonomous_controller
        self.basic_controller = VoitureController()
        self._setup_routes()

    def _setup_routes(self):
        self.app.add_url_rule('/', view_func=self.index)
        self.app.add_url_rule('/action', view_func=self.handle_action, methods=['POST'])
        # Nouvelle route d'API pour obtenir les distances
        self.app.add_url_rule('/api/distances', view_func=self.api_distances, methods=['GET'])

    def index(self):
        return render_template('web.html')

    def handle_action(self):
        action = request.form.get('action')
        if action == 'lancer':
            print("🚀 Lancement de la voiture en mode autonome")
            thread = threading.Thread(target=self.autonomous_controller.run)
            thread.start()
        elif action == 'reset':
            print("🔄 Réinitialisation et relancement (non implémenté)")
        elif action == 'avancer':
            print("➡️ Avancer la voiture en mode simple")
            thread = threading.Thread(target=self.basic_controller.lancer_voiture)
            thread.start()
        return redirect(url_for('index'))

    def api_distances(self):
        """
        Route API renvoyant les mesures des capteurs de distance au format JSON.
        
        QUI: Anthony Vergeylen
        QUOI: Utilise la méthode get_distances() de ControllerCar pour obtenir et retourner les distances.
        QUAND: 09-04-2025
        """
        distances = self.autonomous_controller.get_distances()
        return jsonify(distances)

    def run(self):
        print(f"🌐 Lancement du serveur web sur {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port)

if __name__ == '__main__':
    server = VoitureServer()
    server.run()
