#!/usr/bin/env python3
"""
serveur_voiture.py
------------------
Ce module fournit une interface web via Flask pour contrôler la voiture.
Les actions possibles incluent la rotation sur place, le réinitialisation et
l'avancée de la voiture.

Auteur : Anthony Vergeylen
Date   : 08-04-2025
Quoi   : Permet de contrôler la voiture via une interface web.
"""

from flask import Flask, render_template, request, redirect, url_for
import threading
import time
from moteur import MotorController  # Module personnalisé pour contrôler les moteurs
import RPi.GPIO as GPIO


class VoitureController:
    """
    Classe pour contrôler les mouvements de la voiture.
    
    QUI: Anthony Vergeylen
    QUAND: 08-04-2025
    QUOI: Fournit des méthodes pour manipuler la voiture, notamment la rotation sur place.
    """
    def __init__(self, duration=10, speed=100):
        """
        Initialise le contrôleur de la voiture.
        
        :param duration: Durée de la rotation en secondes (par défaut : 10).
        :param speed: Vitesse de rotation (entre 0 et 100, par défaut : 100).
        
        QUI: Anthony Vergeylen
        QUAND: 08-04-2025
        QUOI: Prépare l'instance pour contrôler les moteurs de la voiture.
        """
        self.duration = duration
        self.speed = speed
        self.motor = MotorController()

    def tourner_sur_place(self):
        """
        Fait tourner la voiture sur elle-même pendant la durée spécifiée.
        
        QUI: Anthony Vergeylen
        QUAND: 08-04-2025
        QUOI: Active les moteurs pour faire tourner la voiture sur elle-même, puis arrête le mouvement.
        """
        try:
            print("🔁 Rotation sur place...")
            # Calcul de la valeur PWM en fonction de la vitesse
            pwm_val = self.motor._MotorController__scale_speed(self.speed)
            # Faire tourner la voiture : un moteur en avant et l'autre en arrière
            self.motor._MotorController__apply_motor_state(
                self.motor._MotorController__moteur0_pin_a,
                self.motor._MotorController__moteur0_pin_b,
                pwm_val
            )
            self.motor._MotorController__apply_motor_state(
                self.motor._MotorController__moteur1_pin_a,
                self.motor._MotorController__moteur1_pin_b,
                -pwm_val
            )
            time.sleep(self.duration)
            print("🛑 Arrêt du mouvement")
            self.motor.stop()
        except Exception as e:
            print("Erreur pendant la rotation :", e)
        finally:
            GPIO.cleanup()
            print("Nettoyage des GPIO terminé.")


class VoitureServer:
    """
    Classe pour gérer le serveur web de contrôle de la voiture.
    
    QUI: Anthony Vergeylen
    QUAND: 08-04-2025
    QUOI: Permet d'interagir avec la voiture via une interface web et d'exécuter les actions correspondantes.
    """
    def __init__(self, host='0.0.0.0', port=5000):
        """
        Initialise le serveur web et configure les routes Flask.
        
        :param host: Adresse IP pour héberger le serveur (par défaut : '0.0.0.0').
        :param port: Port pour le serveur (par défaut : 5000).
        
        QUI: Anthony Vergeylen
        QUAND: 08-04-2025
        QUOI: Prépare l'application Flask et associe les routes aux actions du contrôleur de la voiture.
        """
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.controller = VoitureController()
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
          - 'lancer' : Lancer la rotation sur place dans un thread séparé.
          - 'reset'  : (À implémenter) Réinitialiser et relancer la voiture.
          - 'avancer': (À implémenter) Faire avancer la voiture.
        
        QUI: Anthony Vergeylen
        QUAND: 08-04-2025
        QUOI: Exécute la fonction appropriée selon l'action demandée par l'utilisateur.
        """
        action = request.form.get('action')
        if action == 'lancer':
            print("🚀 Lancement de la voiture")
            # Démarrer la rotation sur place dans un thread pour ne pas bloquer le serveur Flask
            thread = threading.Thread(target=self.controller.tourner_sur_place)
            thread.start()
        elif action == 'reset':
            print("🔄 Réinitialisation et relancement")
            # Logique de réinitialisation à implémenter
        elif action == 'avancer':
            print("➡️ Avancer la voiture")
            # Logique pour faire avancer la voiture à implémenter
        return redirect(url_for('index'))

    def run(self):
        """
        Démarre le serveur web Flask sur l'adresse et le port spécifiés.
        
        QUI: Anthony Vergeylen
        QUAND: 08-04-2025
        QUOI: Lance le serveur pour l'accès via un navigateur.
        """
        print(f"🌐 Lancement du serveur web sur {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port)


if __name__ == '__main__':
    server = VoitureServer()
    server.run()
