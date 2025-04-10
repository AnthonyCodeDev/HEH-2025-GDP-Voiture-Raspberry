import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ajouter le dossier 'src' au chemin d'import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from sensors.ultrasound_sensor import UltrasoundSensor


class TestUltrasoundSensor(unittest.TestCase):
    
    @patch('sensors.ultrasound_sensor.DistanceSensor', autospec=True)
    def setUp(self,mock_distance_sensor):
        # Mock la classe DistanceSensor
        self.mock_distance_sensor = mock_distance_sensor

        # Crée une instance simulée d'UltrasoundSensor avec des pins fictifs
        self.sensor = UltrasoundSensor(name="front", pins=[17, 18])

        # Simule la distance (attribut .distance de DistanceSensor)
        self.sensor.distance = MagicMock(return_value=0.1)  # 10 cm

    def test_calculate_distance_valid(self):
        self.sensor.distance = 0.1  # 10 cm
        result = self.sensor.calculate_distance()
        self.assertEqual(result, 10)

    def test_calculate_distance_below_min(self):
        self.sensor.distance = 0.01  # 1 cm
        with self.assertRaises(ValueError):
            self.sensor.calculate_distance()

    def test_calculate_distance_above_max(self):
        self.sensor.distance = 4.5  # 450 cm
        with self.assertRaises(ValueError):
            self.sensor.calculate_distance()

    def test_calculate_distance_exact_min(self):
        self.sensor.distance = 0.02  # 2 cm
        result = self.sensor.calculate_distance()
        self.assertAlmostEqual(result, 2.0, delta=0.1)

    def test_calculate_distance_exact_max(self):
        self.sensor.distance = 4.0  # 400 cm
        result = self.sensor.calculate_distance()
        self.assertAlmostEqual(result, 400.0, delta=0.1)

if __name__ == '__main__':
    unittest.main()