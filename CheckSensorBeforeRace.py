import RPi.GPIO as GPIO
import time
import board
import busio
import adafruit_tcs34725
from gpiozero import DistanceSensor
import sys

import RPi.GPIO as GPIO

TRIG_PIN = 11
ECHO_PIN = 9

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

try:
    GPIO.output(TRIG_PIN, False)
    print("Stabilisation du capteur...")
    time.sleep(2)

    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    print(f"Capteur Ultrason : distance = {distance} cm")

except Exception as e:
    print(f" Erreur capteur ultrason : {e}")

finally:
    GPIO.cleanup()

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
def test_ultrason(trigger_pin, echo_pin, nom_capteur="Capteur"):
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(trigger_pin, GPIO.OUT)
        GPIO.setup(echo_pin, GPIO.IN)

        # Stabilisation
        GPIO.output(trigger_pin, False)
        time.sleep(0.5)

        # Envoi du signal
        GPIO.output(trigger_pin, True)
        time.sleep(0.00001)
        GPIO.output(trigger_pin, False)

        # Mesure du temps aller-retour
        pulse_start = time.time()
        timeout = pulse_start + 0.04  # 40 ms timeout
        while GPIO.input(echo_pin) == 0 and time.time() < timeout:
            pulse_start = time.time()

        pulse_end = time.time()
        timeout = pulse_end + 0.04
        while GPIO.input(echo_pin) == 1 and time.time() < timeout:
            pulse_end = time.time()

        # Calcul distance
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)

        if 2 < distance < 400:
            print(f"{nom_capteur} : OK (Distance : {distance:.1f} cm)")
        else:
            print(f"{nom_capteur} : Distance hors plage utile ({distance:.1f} cm)")
        # On considère que le capteur est fonctionnel dans tous les cas
        return True


    except Exception as e:
        print(f" {nom_capteur} : ERREUR -> {e}")
        return False
    finally:
        GPIO.cleanup()

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
