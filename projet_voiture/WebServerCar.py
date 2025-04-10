#!/usr/bin/env python3
"""
WebServerCar.py
--------------------
Ce module fournit une interface web via Flask pour contrôler la voiture.
Les actions possibles incluent :
  - 'lancer'  : Lancer la voiture en mode autonome via ControllerCar.
  - 'avancer' : Faire avancer la voiture en mode simple via VoitureController.
  - 'reset'   : (Non implémenté pour l'instant)

De plus, une API est fournie pour obtenir dynamiquement les mesures des capteurs de distance et la vitesse.

Auteur : Anthony Vergeylen
Date   : 08-04-2025
Quoi   : Permet de contrôler la voiture via une interface web et d'accéder aux mesures des capteurs.
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
import threading
import RPi.GPIO as GPIO
from ControllerCar import ControllerCar
from VoitureController import VoitureController

class VoitureServer:
    def __init__(self, host='0.0.0.0', port=5000, autonomous_controller=None, car_launcher=None):
        self.host = host
        self.port = port
        self.app = Flask(__name__, template_folder='templates')
        self.car_launcher = car_launcher
        if autonomous_controller is None:
            self.autonomous_controller = ControllerCar()
        else:
            self.autonomous_controller = autonomous_controller
        self.basic_controller = VoitureController()
        self._setup_routes()

    def _setup_routes(self):
        self.app.add_url_rule('/', view_func=self.index)
        self.app.add_url_rule('/action', view_func=self.handle_action, methods=['POST'])
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
        elif action == 'arreter':
            print("🛑 Arrêt demandé via interface web")
            self.car_launcher.shutdown()
        elif action == 'relancer':
            print("🔄 Relance du module : réinitialisation du système en cours...")
            # Arrêt en douceur des moteurs (sans quitter le programme)
            self.autonomous_controller.motor_ctrl.stop()
            # Réinitialisation de la vitesse
            self.autonomous_controller.current_speed = 0.0

            # Récupération du contrôleur de servo et de la position centrale
            servo = self.autonomous_controller.servo_ctrl
            central = self.autonomous_controller.angle_central

            # Exécution d'une séquence de réinitialisation similaire à celle du main.py
            try:
                import time
                servo.setToDegree(central)
                time.sleep(0.3)
                servo.setToDegree(0)
                time.sleep(0.3)
                servo.setToDegree(central)
                time.sleep(0.3)
                servo.setToDegree(90)
                time.sleep(0.3)
                servo.setToDegree(central)
                time.sleep(0.3)
                servo.disable_pwm()
            except Exception as e:
                print("Erreur lors de la réinitialisation du servo :", e)

            print("🔄 Module relancé, en attente d'une commande de démarrage (LED verte ou bouton start).")
        
        return redirect(url_for('index'))


    def api_distances(self):
        distances = self.autonomous_controller.get_distances()
        speed = self.autonomous_controller.get_speed()
        return jsonify({
            "front": distances["front"],
            "left": distances["left"],
            "right": distances["right"],
            "speed": speed
        })

    def run(self):
        print(f"🌐 Lancement du serveur web sur {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port)