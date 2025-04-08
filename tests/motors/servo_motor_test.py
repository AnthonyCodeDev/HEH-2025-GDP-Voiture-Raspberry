import unittest
from unittest.mock import patch, MagicMock
import sys
import os


# Ajout du chemin vers le dossier src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
from motors.servo_motor import ServoMotor

class TestServoMotor(unittest.TestCase):

    @patch('motors.servo_motor.Servo')  # on ne patch que Servo, car c’est le seul utilisé
    def setUp(self, mock_servo):
        self.mock_servo_instance = MagicMock()
        mock_servo.return_value = self.mock_servo_instance
        self.servo = ServoMotor(pin=0) 

    def test_tourner_max_droite(self):
        self.servo.set_angle(135)
        self.assertAlmostEqual(self.mock_servo_instance.value, 0.5, delta=0.01)
        
    def test_tourner_max_gauche(self):
        self.servo.set_angle(45)
        self.assertAlmostEqual(self.mock_servo_instance.value, -0.5, delta=0.01)

    def test_tourner_positions_invalides(self):
        nom = str("droite")
        for invalide in [ 44, 136]:
            with self.subTest(valeur=invalide):
                with self.assertRaises(ValueError):
                    self.servo.set_angle(invalide)
        for invalide in [nom, None,3.14]:
            with self.subTest(valeur=invalide):
                with self.assertRaises(TypeError):
                    self.servo.set_angle(invalide)

if __name__ == '__main__':
    unittest.main()
