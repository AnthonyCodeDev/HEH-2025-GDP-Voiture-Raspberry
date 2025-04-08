import time
import warnings
from multiprocessing import Process, Queue
from gpiozero import DistanceSensor
from gpiozero.pins.pigpio import PiGPIOFactory

warnings.filterwarnings("ignore")
factory = PiGPIOFactory()

# Paires GPIO à tester (capteurs CD1, CD2, CD3 uniquement)
test_pairs = [
    (11, 9),   # CD1
    (6, 5),    # CD2
    (26, 19)   # CD3
]

# Fonction exécutée dans un processus séparé
def try_sensor(trig, echo, q):
    try:
        sensor = DistanceSensor(echo=echo, trigger=trig, pin_factory=factory, max_distance=4)
        time.sleep(0.2)
        distance = sensor.distance * 100
        sensor.close()
        if 2 <= distance <= 400:
            q.put(distance)
        else:
            q.put(None)
    except:
        q.put(None)

print("🚀 Démarrage du test des capteurs CD1, CD2, CD3...\n")
results = []

for trig, echo in test_pairs:
    print(f"🔄 Test TRIG={trig}, ECHO={echo} ... ", end="")
    q = Queue()
    p = Process(target=try_sensor, args=(trig, echo, q))
    p.start()
    p.join(timeout=2)

    if p.is_alive():
        p.terminate()
        p.join()
        print("❌ Timeout (bloqué)")
    else:
        result = q.get()
        if result is not None:
            print(f"✅ Réponse ! Distance = {result:.2f} cm")
            results.append((trig, echo, result))
        else:
            print("❌ Aucune mesure")

print("\n🧾 Résumé des capteurs détectés :")
if results:
    for trig, echo, dist in results:
        print(f"→ TRIG={trig}, ECHO={echo} → {dist:.2f} cm")
else:
    print("❌ Aucun capteur fonctionnel détecté.")

print("\n🔁 Fin du scan.")
