import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from composants.UltrasoundSensor import UltrasoundSensor

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class TestUltrasoundSensor(unittest.TestCase):
    
    @patch('composants.UltrasoundSensor.DistanceSensor', autospec=True)
    def setUp(self,mock_distance_sensor):
        # Mock la classe DistanceSensor
        #self.mock_distance_sensor = mock_distance_sensor

        self.mock_distance_sensor_instance = mock_distance_sensor.return_value

        # Crée une instance simulée d'UltrasoundSensor avec des pins fictifs
        self.sensor = UltrasoundSensor(name="front", pins=[17, 18])

        # Simule la distance (attribut .distance de DistanceSensor)
        #self.distance = self.sensor.getSensor().distance = MagicMock(return_value=0.1)  # 10 cm

    def test_calculate_distance_valid(self):
        #self.distance = 0.1  # 10 cm
        self.mock_distance_sensor_instance.distance = 0.1
        result = self.sensor.read_data()
        self.assertEqual(result, 10)

    def test_calculate_distance_below_min(self):
        self.mock_distance_sensor_instance.distance = 0.01  
        with self.assertRaises(ValueError):
            self.sensor.read_data()

    def test_calculate_distance_above_max(self):
        self.mock_distance_sensor_instance.distance = 4.5  # 450 cmµ
        with self.assertRaises(ValueError):
            self.sensor.read_data()

    def test_calculate_distance_exact_min(self):
        self.mock_distance_sensor_instance.distance = 0.02  # 2 cm
        result = self.sensor.read_data()
        self.assertAlmostEqual(result, 2.0, delta=0.1)

    def test_calculate_distance_exact_max(self):
        self.mock_distance_sensor_instance.distance = 4.0  # 400 cm
        result = self.sensor.read_data()
        self.assertAlmostEqual(result, 400.0, delta=0.1)

if __name__ == '__main__':
    unittest.main()