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

def test_servo_moteur_basique():
    try:
        pwm = PCA.PWM()
        pwm.frequency = 60
        pwm.write(0, 0, 45)  # Position neutre
        time.sleep(0.3)
        pwm.write(0, 0, 60)  # Petit déplacement
        time.sleep(0.3)
        pwm.write(0, 0, 45)  # Retour centre
        time.sleep(0.3)
        pwm.write(0, 0, 4096)  # Désactive le signal
        print(" Servo moteur : OK")
        return True
    except Exception as e:
        print(f" Servo moteur : ERREUR -> {e}")
        return False

def test_hcsr04(TRIG, ECHO, place):
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(TRIG, GPIO.OUT)
        GPIO.setup(ECHO, GPIO.IN)

        # S'assurer que TRIG est bas
        GPIO.output(TRIG, False)
        time.sleep(0.5)

        # Envoi d’une impulsion TRIG
        GPIO.output(TRIG, True)
        time.sleep(0.00001)  # 10 µs
        GPIO.output(TRIG, False)

        # Mesure du temps de réponse sur ECHO
        timeout = time.time() + 0.05  # 50 ms timeout

        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
            if pulse_start > timeout:
                raise TimeoutError("Aucune réponse du capteur (ECHO reste bas)")
                return False

        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
            if pulse_end - pulse_start > 0.025:  # au-delà de 4m (~25ms)
                raise TimeoutError("Durée d'impulsion trop longue")
                return False

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150  # cm
        distance = round(distance, 2)

        print(f"HC-SR04 {place} OK - Distance mesurée : {distance} cm")
        return True

    except Exception as e:
        print(f"Capteur HC-SR04 {place} ERREUR : {e}")
        return False

    finally:
        GPIO.cleanup()
        
def main():
    print("Vérification des capteurs en cours\n")

    gpio_ok = test_gpio_moteur([17, 18, 27, 22])
    rgb_ok = test_rgb_sensor()
    hcsr_droit = test_hcsr04(26,19, "DROIT")
    hcsr_avant = test_hcsr04(6,5, 'AVANT')
    hcsr_gauche = test_hcsr04(11,9, 'GAUCHE')


if __name__ == "__main__":
    main()
