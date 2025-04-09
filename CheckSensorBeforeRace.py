import RPi.GPIO as GPIO
import time
import board
import busio
import adafruit_tcs34725
from gpiozero import DistanceSensor
import sys

import RPi.GPIO as GPIO


import RPi.GPIO as GPIO
import time

def test_ultrason(trigger_pin, echo_pin, nom_capteur="Capteur"):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(trigger_pin, GPIO.OUT)
    GPIO.setup(echo_pin, GPIO.IN)

    try:
        GPIO.output(trigger_pin, False)
        print("Stabilisation du capteur...")
        time.sleep(2)  # Stabilisation du capteur

        # Envoi de l'impulsion
        GPIO.output(trigger_pin, True)
        time.sleep(0.00001)  # 10 microsecondes
        GPIO.output(trigger_pin, False)

        # Attente de l'écho
        pulse_start = time.time()
        while GPIO.input(echo_pin) == 0:
            pulse_start = time.time()  # Enregistrer l'instant du début de l'écho

        pulse_end = time.time()
        while GPIO.input(echo_pin) == 1:
            pulse_end = time.time()  # Enregistrer l'instant de fin de l'écho

        # Calcul de la durée de l'écho
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150  # Calcul de la distance
        distance = round(distance, 2)

        if distance <= 0 or distance > 400:
            print(f"Erreur : distance {distance} cm hors de la plage utile pour {nom_capteur}.")
        else:
            print(f"Capteur {nom_capteur} : distance = {distance} cm")

    except Exception as e:
        print(f"Erreur capteur {nom_capteur} : {e}")

    finally:
        GPIO.cleanup()  # Nettoyage des GPIO



# --- Vérification GPIO moteurs ---
def test_gpio_moteur(pins):
    try:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(pin, GPIO.LOW)
        print(" GPIO moteurs : OK")
        return True
    except Exception as e:
        print(f" GPIO moteurs : ERREUR -> {e}")
        return False
    finally:
        GPIO.cleanup()

# --- Vérification capteur RGB ---
def test_rgb_sensor():
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        capteur = adafruit_tcs34725.TCS34725(i2c)
        capteur.enable = True
        capteur.integration_time = 100
        r, g, b = capteur.color_rgb_bytes
        if (r + g + b) == 0:
            raise ValueError("Valeurs RGB nulles")
        print(f" Capteur RGB : OK (R={r}, G={g}, B={b})")
        return True
    except Exception as e:
        print(f" Capteur RGB : ERREUR -> {e}")
        return False

# --- Vérification capteurs ultrason ---
"""def test_ultrason(trigger_pin, echo_pin, nom_capteur="Capteur"):
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(trigger_pin, GPIO.OUT)
        GPIO.setup(echo_pin, GPIO.IN)

        print(f"Stabilisation du {nom_capteur}...")
        time.sleep(0.5)

        max_essais = 5
        for essai in range(max_essais):
            # Envoi de l'impulsion
            GPIO.output(trigger_pin, False)
            time.sleep(0.1)
            GPIO.output(trigger_pin, True)
            time.sleep(0.1)
            GPIO.output(trigger_pin, False)

            # Attente de l écho
            debut = time.time()
            timeout = debut + 0.04
            while GPIO.input(echo_pin) == 0 and time.time() < timeout:
                debut = time.time()

            fin = time.time()
            timeout = fin + 0.04
            while GPIO.input(echo_pin) == 1 and time.time() < timeout:
                fin = time.time()

            # Calcul de la distance
            duree = fin - debut
            distance = round(duree * 17150, 2)

            # Vérification de la validité de la mesure
            if 2 <= distance <= 400:
                print(f"{nom_capteur} : OK (Distance : {distance} cm)")
                return True
            else:
                print(f"{nom_capteur} : mesure incorrecte ({distance} cm), nouvel essai...")

        print(f"{nom_capteur} : Échec après {max_essais} tentatives.")
        return False

    except Exception as e:
        print(f"{nom_capteur} : ERREUR -> {e}")
        return False

    finally:
        GPIO.cleanup()"""


def main():
    print("Vérification des capteurs en cours...\n")

    gpio_ok = test_gpio_moteur([17, 18, 27, 22])
    rgb_ok = test_rgb_sensor()
    
    print(" Vérification des capteurs à ultrasons...\n")
    us1_ok = test_ultrason(trigger_pin=23, echo_pin=24, nom_capteur="Ultrason 1")
    us2_ok = test_ultrason(trigger_pin=20, echo_pin=21, nom_capteur="Ultrason 2")
    us3_ok = test_ultrason(trigger_pin=19, echo_pin=26, nom_capteur="Ultrason 3")

    if us1_ok and us2_ok and us3_ok:
        print("\n Tous les capteurs ultrasons fonctionnent.")
    else:
        print("\n Un ou plusieurs capteurs ultrasons ne répondent pas.")
    if us1_ok and us2_ok and us3_ok:
        print("\n Tous les capteurs ultrasons fonctionnent.")
    else:
        print("\n Un ou plusieurs capteurs ultrasons ne répondent pas.")
    all_ok = gpio_ok and rgb_ok and us1_ok and us2_ok and us3_ok
    if all_ok:
        print("\n Tous les capteurs sont prêts pour la course.")
    else:
        print("\n Des erreurs ont été détectées. Veuillez vérifier les branchements et l'alimentation.")

if __name__ == "__main__":
    main()
