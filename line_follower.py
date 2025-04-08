from gpiozero import DigitalInputDevice
from time import sleep

# Configuration du capteur
capteur_ligne = DigitalInputDevice(20)  # GPIO BCM 20 (pin physique 38)

try:
    while True:
        if capteur_ligne.is_active:
            print("➡️ Surface claire détectée (blanc)")
        else:
            print("⬛ Surface noire détectée (ligne suivie)")
        sleep(0.5)  # Délai pour éviter de spam la console
except KeyboardInterrupt:
    print("Arrêt manuel du programme")
