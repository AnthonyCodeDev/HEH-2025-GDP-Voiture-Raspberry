from gpiozero import Motor
from .i_motor import Imotor

class DcMotor(Imotor):
    def __init__(self, forward, backward, *, enable=None, pwm=True, pin_factory=None):
        # Vérification si les broches forward et backward sont valides
        if forward is None or backward is None:
            raise ValueError("Les broches 'forward' et 'backward' doivent être spécifiées et non None.")
        
        self.motor = Motor(forward=forward, backward=backward, enable=enable, pwm=pwm, pin_factory=pin_factory)
        self._speed = 0  # Valeur entre -1 (arrière) et 1 (avant)

    def set_speed(self, speed: float):
        """
        Définit la vitesse du moteur :
        - 1.0 = pleine vitesse avant
        - 0 = stop
        - -1.0 = pleine vitesse arrière
        """
        if not isinstance(speed, (int, float)):
            raise TypeError("La vitesse doit être un nombre (int ou float).")

        if not (-1 <= speed <= 1):
            raise ValueError("La vitesse doit être comprise entre -1 et 1.")

        self._speed = speed

        if speed > 0:
            self.motor.forward(speed)
        elif speed < 0:
            self.motor.backward(-speed)
        else:
            self.motor.stop()

    def read_data(self):
        return {
            "is_active": self.motor.is_active,
            "speed": self._speed
        }

    def display_data(self):
        if self.motor.is_active:
            direction = "forward" if self._speed > 0 else "backward"
            print(f"Motor running {direction} at speed {abs(self._speed):.2f}")
        else:
            print("Motor is stopped")

    def forward(self):
        self.set_speed(1)

    def backward(self):
        self.set_speed(-1)

    def stop(self):
        self.set_speed(0)
