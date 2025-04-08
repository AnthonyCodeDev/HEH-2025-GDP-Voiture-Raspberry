from gpiozero import Servo
from .i_motor import Imotor  # Interface du moteur, si elle existe

class ServoMotor(Imotor):
    """
    Contrôle d'un servo-moteur via gpiozero.
    
    L'angle est géré en degrés (0 à 135) :
      - 0° correspond à servo.value = -1  (braquage max à gauche)
      - 90° correspond à servo.value = 0  (centré)
      - 135° correspond à servo.value = 1  (braquage max à droite)
    """

    def __init__(self, pin, min_pulse_width=0.0005, max_pulse_width=0.0025):
        self.servo = Servo(pin, min_pulse_width=min_pulse_width, max_pulse_width=max_pulse_width)

    def set_angle(self, angle: float):
        """
        Positionne le servo à l'angle spécifié (de 0° à 135°).
        """
        if not isinstance(angle, (int, float)):
            raise TypeError("L'angle doit être un nombre (int ou float).")

        if not (0 <= angle <= 135):
            raise ValueError("L'angle doit être compris entre 0 et 135 degrés.")

        # Conversion de l'angle 0–135° en valeur entre -1 à +1
        self.servo.value = (angle - 67.5) / 67.5  # 0° -> -1 et 135° -> +1

    def read_data(self):
        """
        Retourne l'angle actuel estimé du servo (entre 0 et 135°).
        Si la valeur est None, retourne 67.5° (centré).
        """
        if self.servo.value is None:
            return 67.5  # centre si aucune valeur n'est définie
        return (self.servo.value * 67.5) + 67.5  # Mapping inverse : -1 → 0°, 0 → 67.5°, 1 → 135°

    def display_data(self):
        """
        Affiche l'angle actuel du servo.
        """
        current_angle = self.read_data()
        print(f"Angle actuel du servo : {current_angle:.1f}°")

