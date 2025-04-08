#!/usr/bin/env python3
from gpiozero import LED
from time import sleep

# On utilise ici la classe LED (une simple sortie digitale)
# qui convient pour activer/désactiver les enable du L298N.
# Moteur 1 (sur la pin GPIO 5)
moteur1 = LED(1)
# Moteur 2 (sur la pin GPIO 4)
moteur2 = LED(6)

# Fonction pour démarrer les moteurs en avant
def demarrer_moteurs():
    print("Démarrage en avant des moteurs...")
    moteur1.on()  # active le moteur 1 (direction fixée en interne)
    moteur2.on()  # active le moteur 2
    # Les moteurs tournent à pleine puissance,
    # si une commande de vitesse PWM est nécessaire, il faudrait utiliser PWMOutputDevice

# Fonction pour arrêter les moteurs
def arreter_moteurs():
    print("Arrêt des moteurs.")
    moteur1.off() # stop le moteur 1
    moteur2.off() # stop le moteur 2

if __name__ == "__main__":
    try:
        # Démarrer les moteurs en avant
        demarrer_moteurs()
        # Laisser tourner pendant 5 secondes
        sleep(5)
        # Arrêter les moteurs
        arreter_moteurs()

    except KeyboardInterrupt:
        # Arrêt en cas d'interruption (Ctrl+C)
        arreter_moteurs()
        print("Programme interrompu par l'utilisateur.")
