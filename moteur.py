from dcmotor import DCMotor
from machine import Pin, PWM
from time import sleep

# Fréquence pour le signal PWM
frequency = 15000

# Définition des broches selon le câblage utilisé (à adapter si besoin)
pin1 = Pin(5, Pin.OUT)     # IN1
pin2 = Pin(4, Pin.OUT)     # IN2
enable = PWM(Pin(13), freq=frequency)  # ENA (PWM)

# Création de l'objet moteur
dc_motor = DCMotor(pin1, pin2, enable)

# Mouvement vers l'avant à 70% de vitesse
print("🚗 Avance")
dc_motor.forward(70)
sleep(3)

# Mouvement en arrière à 60% de vitesse
print("🔙 Recule")
dc_motor.backwards(60)
sleep(3)

# Arrêt du moteur
print("🛑 Arrêt")
dc_motor.stop()

# Fin du script
print("✅ Fin du programme")
