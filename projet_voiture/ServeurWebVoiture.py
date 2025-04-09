#!/usr/bin/env python3
"""
ServeurWebVoiture.py
--------------------
Ce module fournit une interface web via Flask pour contrôler la voiture.
Les actions possibles incluent :
  - 'lancer'  : Lancer la voiture en mode autonome via CarController (contrôle complet de la navigation).
  - 'avancer' : Faire avancer la voiture en mode basique (commandé par VoitureController).
  - 'reset'   : Réinitialisation et relancement (non implémenté pour l'instant).

Auteur : Anthony Vergeylen
Date   : 08-04-2025
Quoi   : Permet de contrôler la voiture via une interface web.
"""

from flask import Flask, render_template, request, redirect, url_for
import threading
import time
from MotorController import MotorController  # Module personnalisé pour contrôler les moteurs
import RPi.GPIO as GPIO
from CarController import CarController     # Module de contrôle autonome de la voiture

class VoitureController:
    """
    Classe pour contrôler la voiture en mode basique.
    
    QUI: Anthony Vergeylen
    QUAND: 08-04-2025
    QUOI: Fournit une méthode pour faire avancer la voiture en ligne droite.
    """
    def __init__(self, duration=10, speed=100):
        """
        Initialise le contrôleur de la voiture en mode simple.
        
        :param duration: Durée pendant laquelle la voiture avance (par défaut : 10 secondes).
        :param speed: Vitesse de la voiture (entre 0 et 100, par défaut : 100).
        
        QUI: Anthony Vergeylen
        QUAND: 08-04-2025
        QUOI: Prépare le contrôleur basique pour envoyer les commandes moteurs.
        """
        self.duration = duration
        self.speed = speed
        self.motor = MotorController()

    def lancer_voiture(self):
        """
        Lance la voiture en la faisant avancer en ligne droite pendant une durée fixée.
        
        QUI: Anthony Vergeylen
        QUAND: 08-04-2025
        QUOI: Active la commande de la voiture pour avancer (via MotorController.forward),
              puis arrête la voiture après la durée définie.
        """
        try:
            print("🚀 Lancement de la voiture en mode avance...")
            # On suppose ici que MotorController possède une méthode forward(speed)
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
    QUAND: 08-04-2025
    QUOI: Permet d'interagir avec la voiture via une interface web en utilisant une instance partagée de CarController.
    """
    def __init__(self, host='0.0.0.0', port=5000, autonomous_controller=None):
        """
        Initialise le serveur web et configure les routes Flask.
        
        :param autonomous_controller: Instance de CarController à utiliser. Si None, une nouvelle instance sera créée.
        """
        self.host = host
        self.port = port
        self.app = Flask(__name__, template_folder='templates')
        if autonomous_controller is None:
            from CarController import CarController  # Importe ici au cas où
            self.autonomous_controller = CarController()
        else:
            self.autonomous_controller = autonomous_controller
        self.basic_controller = VoitureController()  # Pour la commande simple
        self._setup_routes()

    def _setup_routes(self):
        """
        Configure les routes pour l'application Flask.
        
        QUI: Anthony Vergeylen
        QUAND: 08-04-2025
        QUOI: Définit les points d'accès HTTP pour l'interface utilisateur.
        """
        self.app.add_url_rule('/', view_func=self.index)
        self.app.add_url_rule('/action', view_func=self.handle_action, methods=['POST'])

    def index(self):
        """
        Affiche la page d'accueil contenant l'interface web.
        
        QUI: Anthony Vergeylen
        QUAND: 08-04-2025
        QUOI: Retourne le template 'web.html' pour l'interaction utilisateur.
        """
        return render_template('web.html')

    def handle_action(self):
        """
        Traite les actions envoyées via le formulaire web.
        
        Les actions gérées sont :
          - 'lancer' : Lance la voiture en mode autonome en appelant la méthode run() de CarController.
          - 'reset'  : (À implémenter) Réinitialiser et relancer la voiture.
          - 'avancer': Fait avancer la voiture en mode simple via VoitureController.
        
        QUI: Anthony Vergeylen
        QUAND: 08-04-2025
        QUOI: Exécute la fonction appropriée selon l'action demandée par l'utilisateur.
        """
        action = request.form.get('action')
        if action == 'lancer':
            print("🚀 Lancement de la voiture en mode autonome")
            # Lancer la voiture via le contrôle autonome (CarController)
            thread = threading.Thread(target=self.autonomous_controller.run)
            thread.start()
        elif action == 'reset':
            print("🔄 Réinitialisation et relancement (non implémenté)")
            # Logique de réinitialisation à implémenter
        elif action == 'avancer':
            print("➡️ Avancer la voiture en mode simple")
            thread = threading.Thread(target=self.basic_controller.lancer_voiture)
            thread.start()
        return redirect(url_for('index'))

    def run(self):
        """
        Démarre l'application Flask sur l'adresse et le port spécifiés.
        
        QUI: Anthony Vergeylen
        QUAND: 08-04-2025
        QUOI: Lance le serveur pour l'accès via un navigateur.
        """
        print(f"🌐 Lancement du serveur web sur {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port)


if __name__ == '__main__':
    server = VoitureServer()
    server.run()
