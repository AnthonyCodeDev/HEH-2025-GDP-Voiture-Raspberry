from gpiozero import Motor
from time import sleep

# Définir le moteur avec les bonnes broches IN1 et IN2
# (ici GPIO 17 = IN1, GPIO 27 = IN2)
motor = Motor(forward=5, backward=4)

# Avancer pendant 3 secondes
print("🚗 Avance")
motor.forward()
sleep(3)

# Reculer pendant 3 secondes
print("🔙 Recule")
motor.backward()
sleep(3)

# Arrêter le moteur
print("🛑 Arrêt")
motor.stop()

print("✅ Fin du programme")
