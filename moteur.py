from gpiozero import Motor, PWMOutputDevice
from time import sleep

# Configuration selon ton schéma (A5)
# GPIO 18 = IN1, GPIO 19 = IN2, GPIO 17 = PWM (ENA)
motor = Motor(forward=18, backward=19)
pwm = PWMOutputDevice(16)

print("🔋 Activation du moteur DC2 (PWM)")
pwm.value = 1.0  # Pleine puissance (entre 0.0 et 1.0)

print("🚗 Avance...")
motor.forward()
sleep(2)

print("⛔ Stop")
motor.stop()
sleep(1)

print("🔁 Recule...")
motor.backward()
sleep(2)

print("🛑 Stop & désactivation PWM")
motor.stop()
pwm.value = 0
