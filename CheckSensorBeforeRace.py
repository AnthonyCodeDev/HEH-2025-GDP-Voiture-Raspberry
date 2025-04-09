import RPi.GPIO as GPIO
import time
import board
import busio
import adafruit_tcs34725
from gpiozero import DistanceSensor
import sys

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

def main():
    print("Vérification des capteurs en cours...\n")

    gpio_ok = test_gpio_moteur([17, 18, 27, 22])
    rgb_ok = test_rgb_sensor()

if __name__ == "__main__":
    main()
