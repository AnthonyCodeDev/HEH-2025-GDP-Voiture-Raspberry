from gpiozero import DistanceSensor
from signal import pause
import time
import sys

# ✅ Broches correctes pour CD1 (d'après ta dernière photo)
TRIG = 26  # Orange
ECHO = 19   # Jaune
 
def auto_check(sensor):
    print("📡 Vérification du capteur HC-SR04 (CD1)...")
    try:
        distance_cm = sensor.distance * 100
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

if __name__ == "__main__":
    capteur = DistanceSensor(echo=ECHO, trigger=TRIG, max_distance=4, threshold_distance=0.1)
    auto_check(capteur)
    boucle_principale(capteur)
