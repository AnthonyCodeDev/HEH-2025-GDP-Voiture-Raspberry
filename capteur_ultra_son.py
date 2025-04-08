from gpiozero import DistanceSensor
from gpiozero.pins.pigpio import PiGPIOFactory
import time

factory = PiGPIOFactory()

# Liste des GPIO disponibles (à adapter si certaines sont utilisées par autre chose)
gpio_list = [5, 6, 9, 11, 19, 20, 21, 23, 24, 25, 26]

def test_combinaison(trigger_pin, echo_pin):
    if trigger_pin == echo_pin:
        return None

    print(f"🔄 Test TRIG={trigger_pin}, ECHO={echo_pin} ... ", end="")
    try:
        sensor = DistanceSensor(echo=echo_pin, trigger=trigger_pin, pin_factory=factory, max_distance=4, threshold_distance=0.1)
        time.sleep(0.1)
        distance = sensor.distance * 100
        if 2 <= distance <= 400:
            print(f"✅ Réponse ! Distance = {distance:.2f} cm")
            return (trigger_pin, echo_pin, distance)
        else:
            print("❌ Pas de mesure")
    except Exception as e:
        print(f"⚠️ Erreur : {e}")
    return None

# Lancer le test de toutes les combinaisons
print("🚀 Démarrage du test de toutes les combinaisons TRIG/ECHO...\n")
resultats = []

for trig in gpio_list:
    for echo in gpio_list:
        res = test_combinaison(trig, echo)
        if res:
            resultats.append(res)
        time.sleep(0.3)

print("\n🧾 Résumé des capteurs détectés :")
if resultats:
    for trig, echo, dist in resultats:
        print(f"→ TRIG={trig}, ECHO={echo} → {dist:.2f} cm")
else:
    print("❌ Aucun capteur détecté.")

print("\n🔁 Fin du scan.")
