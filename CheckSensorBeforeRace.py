import RPi.GPIO as GPIO
import time
import board
import busio
import adafruit_tcs34725
from projet_voiture import PWM as PCA
from gpiozero import DistanceSensor 

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
        return {"Nom": "GPIO moteurs", "Etat": "✅ OK"}
    except Exception as e:
        return {"Nom": "GPIO moteurs", "Etat": f"❌ ERREUR -> {e}"}
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
        return {"Nom": "Capteur RGB", "Etat": f"✅ OK (R={r}, G={g}, B={b})"}
    except Exception as e:
        return {"Nom": "Capteur RGB", "Etat": f"❌ ERREUR -> {e}"}

def test_servo_moteur_presence():
    """
    Test de base : vérifie que le contrôleur PWM est accessible et
    que le servo est alimenté (sans envoyer de position de rotation).
    Aucun mouvement ne sera commandé.
    """
    try:
        pwm = PCA.PWM()            # Initialisation du module PWM
        pwm.frequency = 60         # Fréquence standard pour servos
        time.sleep(0.2)            # Laisse le bus I2C s’initialiser
        pwm.write(0, 0, 4096)      # Coupe le signal sur le canal 0 (désactivation passive)
        return {"Nom": "Servo moteur", "Etat": "✅ OK"}
    except Exception as e:
        return {"Nom": "Servo moteur", "Etat": f"❌ ERREUR -> {e}"}

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
                return {"Nom": f"Capteur HC-SR04 {place}", "Etat": "❌ Timeout"}

        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
            if pulse_end - pulse_start > 0.025:  # au-delà de 4m (~25ms)
                raise TimeoutError("Durée d'impulsion trop longue")
                return {"Nom": f"Capteur HC-SR04 {place}", "Etat": "❌ Durée trop longue"}

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150  # cm
        distance = round(distance, 2)

        return {"Nom": f"Capteur HC-SR04 {place}", "Etat": f"✅ OK - Distance mesurée : {distance} cm"}

    except Exception as e:
        return {"Nom": f"Capteur HC-SR04 {place}", "Etat": f"❌ ERREUR -> {e}"}

    finally:
        GPIO.cleanup()

def main():
    # Lancer les tests des capteurs et stocker les résultats dans une liste
    test_results = []
    test_results.append(test_gpio_moteur([17, 18, 27, 22]))
    test_results.append(test_rgb_sensor())
    test_results.append(test_hcsr04(26, 19, "DROIT"))
    test_results.append(test_hcsr04(6, 5, "AVANT"))
    test_results.append(test_hcsr04(11, 9, "GAUCHE"))
    test_results.append(test_servo_moteur_presence())

    # Retourner un tableau des résultats sous forme de liste de dictionnaires
    return test_results


def afficher_tableau(results):
    # Données de la table
    headers = ["Nom", "Etat"]
    data = [[result["Nom"], result["Etat"]] for result in results]

    # Calcul de la largeur de chaque colonne
    col_widths = [max(len(str(row[i])) for row in [headers] + data) for i in range(len(headers))]

    # Fonction pour formater une ligne
    def format_row(row):
        return "| " + " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)) + " |"

    # Ligne de séparation
    separator = "+-" + "-+-".join("-" * width for width in col_widths) + "-+"

    # Affichage
    print(separator)
    print(format_row(headers))
    print(separator)
    for row in data:
        print(format_row(row))
    print(separator)


if __name__ == "__main__":
    # Appeler la fonction main et récupérer les résultats
    results = main()

    # Afficher les résultats sous forme de tableau
    afficher_tableau(results)
 
