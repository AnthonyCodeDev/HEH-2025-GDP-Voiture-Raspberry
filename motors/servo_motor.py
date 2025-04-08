from gpiozero import Servo
from .i_motor import Imotor  # ou bien une interface IServoMotor si tu en as une

class ServoMotor(Imotor):
    """
    Contrôle d'un servo-moteur via gpiozero.
    
    L'angle est géré en degrés (0 à 180).
    La conversion se fait ainsi : 
      - 0° correspond à servo.value = -1
      - 90° correspond à servo.value = 0
      - 180° correspond à servo.value = 1
    """
    def __init__(self, pin, min_pulse_width=0.0005, max_pulse_width=0.0025):
        # Crée l'objet servo de gpiozero sur la broche spécifiée.
        self.servo = Servo(pin, min_pulse_width=min_pulse_width, max_pulse_width=max_pulse_width)
    
    def set_angle(self, angle: float):
        """
        Positionne le servo à l'angle spécifié (0 à 180 degrés).
        """
        if not (0 <= angle <= 180):
            raise ValueError("L'angle doit être compris entre 0 et 180 degrés.")
        # Conversion de l'angle en valeur entre -1 et 1.
        self.servo.value = (angle - 90) / 90

    def read_data(self):
        """
        Retourne l'angle actuel du servo, basé sur sa valeur.
        Si la valeur n'est pas définie, on retourne 90° par défaut.
        """
        if self.servo.value is None:
            return 90
        # Inverse la conversion : value de -1 à 1 en angle de 0 à 180°
        return (self.servo.value * 90) + 90

    def display_data(self):
        """
        Affiche l'angle actuel du servo.
        """
        current_angle = self.read_data()
        print(f"Angle actuel du servo : {current_angle:.1f}°")
