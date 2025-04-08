from gpiozero import DistanceSensor
from signal import pause
import time
import sys

# Définir les broches (attention : gpiozero attend TRIG puis ECHO dans l'ordre inverse de RPi.GPIO)
TRIG = 11  # Orange
ECHO = 9   # Jaune (modifié selon ta photo — GPIO 21 n'est pas correct)

def auto_check(sensor):
    print("📡 Vérification du capteur HC-SR04...")
    try:
        distance_cm = sensor.distance * 100  # La propriété `.distance` donne des mètres
        if distance_cm > 400 or distance_cm <= 2:
            print("[ERREUR] Distance hors plage ou capteur non détecté.")
            sys.exit(1)
        else:
            print(f"[OK] Capteur actif. Distance mesurée : {round(distance_cm, 2)} cm")
    except Exception as e:
        print(f"[ERREUR] Capteur introuvable ou mal branché : {e}")
        sys.exit(1)

def boucle_principale(sensor):
    try:
        while True:
            distance_cm = sensor.distance * 100
            print(f"Distance : {round(distance_cm, 2)} cm")
            time.sleep(1)
    except KeyboardInterrupt:
        print("⛔ Programme arrêté par l'utilisateur")

# Lancement
if __name__ == "__main__":
    # Création du capteur (gpiozero attend TRIG, puis ECHO)
    capteur = DistanceSensor(echo=ECHO, trigger=TRIG, max_distance=4, threshold_distance=0.1)

    auto_check(capteur)
    boucle_principale(capteur)
