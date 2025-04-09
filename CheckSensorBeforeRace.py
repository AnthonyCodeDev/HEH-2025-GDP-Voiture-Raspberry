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
        print("✅ GPIO moteurs : OK")
        return True
    except Exception as e:
        print(f"❌ GPIO moteurs : ERREUR -> {e}")
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
        print(f"✅ Capteur RGB : OK (R={r}, G={g}, B={b})")
        return True
    except Exception as e:
        print(f"❌ Capteur RGB : ERREUR -> {e}")
        return False

# --- Vérification capteurs ultrason ---
def test_ultrason(nom, trig, echo):
    try:
        sensor = DistanceSensor(trigger=trig, echo=echo, max_distance=4, threshold_distance=0.1)
        time.sleep(0.2)  # petit délai pour stabilisation
        distance_cm = sensor.distance * 100
        if distance_cm < 2 or distance_cm > 400:
            print(f"❌ {nom} : Distance hors plage ({distance_cm:.1f} cm)")
            return False
        else:
            print(f"✅ {nom} : OK ({distance_cm:.1f} cm)")
            return True
    except Exception as e:
        print(f"❌ {nom} : ERREUR -> {e}")
        return False

def main():
    print("🔍 Vérification des capteurs en cours...\n")

    gpio_ok = test_gpio_moteur([17, 18, 27, 22])
    rgb_ok = test_rgb_sensor()
    
    print("\n📡 Vérification des capteurs à ultrasons...")
    us1_ok = test_ultrason("Ultrason 1", trig=11, echo=9)
    us2_ok = test_ultrason("Ultrason 2", trig=26, echo=19)
    us3_ok = test_ultrason("Ultrason 3", trig=6, echo=5)

    all_ok = gpio_ok and rgb_ok and us1_ok and us2_ok and us3_ok
    if all_ok:
        print("\n✅ Tous les capteurs sont prêts pour la course.")
    else:
        print("\n⚠️ Des erreurs ont été détectées. Veuillez vérifier les branchements et l'alimentation.")

if __name__ == "__main__":
    main()
