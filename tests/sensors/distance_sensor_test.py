import unittest
from unittest.mock import patch, MagicMock
from gpiozero.pins.mock import MockFactory
from gpiozero import Device
import sys
import os
import logging

# Ajouter le dossier 'src' au chemin d'import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from projet_voiture.CapteurDistance import CapteurDistance

# configurate logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class TestUltrasoundSensor(unittest.TestCase):
    
    @patch('projet_voiture.CapteurDistance.DistanceSensor')
    def setUp(self, mock_distance_sensor_class):
        Device.pin_factory = MockFactory()
    
        # Création d’un mock de capteur
        mock_sensor_instance = MagicMock()
        mock_sensor_instance.distance = 0.1  # Simule une distance de 10 cm
        mock_distance_sensor_class.return_value = mock_sensor_instance
    
        # Création de l’objet à tester
        self.sensor = CapteurDistance(sensor_sample_count=5, sensor_sample_delay=0.01, max_distance=4.0)
    
        # Configure les capteurs simulés pour retourner des valeurs spécifiques
        self.sensor.sensor_left.get_distance_left = MagicMock(return_value=0.1)  # 10 cm
        self.sensor.sensor_right.get_distance_right = MagicMock(return_value=0.1)  # 10 cm
        self.sensor.sensor_front.get_distance_front = MagicMock(return_value=0.1)  # 10 cm
    
        self.directions = ["left", "right", "front"]

    def test_calculate_distance_valid(self):
        """Teste les distances valides pour chaque orientation."""
        for direction in self.directions:
            with self.subTest(direction=direction):
                # Récupère la méthode get_distance_<direction>
                method = getattr(self.sensor, f"get_distance_{direction}")
                # Appelle la méthode et vérifie le résultat
                result = method()
                logging.info(f"Distance {direction}: {result} cm")
                # Vérifie que la distance est correcte (10 cm avec une tolérance de 0.1 cm)
                self.assertAlmostEqual(result, 10.0, delta=0.1)

    def test_calculate_distance_below_min(self):
        self.sensor.distance = 0.01  # 1 cm
        for direction in self.directions:
            with self.subTest(direction=direction):
                method = getattr(self.sensor, f"get_distance_{direction}")
                with self.assertRaises(ValueError):
                    method()

    def test_calculate_distance_above_max(self):
        self.sensor.distance = 4.5  # 450 cm
        for direction in self.directions:
            with self.subTest(direction=direction):
                method = getattr(self.sensor, f"get_distance_{direction}")
                with self.assertRaises(ValueError):
                    method()

    def test_calculate_distance_exact_min(self):
        self.sensor.distance = 0.02  # 2 cm
        for direction in self.directions:
            with self.subTest(direction=direction):
                method = getattr(self.sensor, f"get_distance_{direction}")
                with self.assertRaises(ValueError):
                    method()

    def test_calculate_distance_exact_max(self):
        self.sensor.distance = 4.0  # 400 cm
        for direction in self.directions:
            with self.subTest(direction=direction):
                method = getattr(self.sensor, f"get_distance_{direction}")
                with self.assertRaises(ValueError):
                    method()

    def test_runtime_error_distance(self):
        self.sensor.distance = MagicMock(side_effect=RuntimeError("Sensor error"))
        for direction in self.directions:
            with self.subTest(direction=direction):
                method = getattr(self.sensor, f"get_distance_{direction}")
                with self.assertRaises(RuntimeError):
                    method()

    def test_with_sample_count_as_zero(self):
        with self.assertRaises(ValueError):
            CapteurDistance(sensor_sample_count=0, sensor_sample_delay=0.01, max_distance=4.0)

    def test_with_sample_delay_as_zero(self):
        with self.assertRaises(ValueError):
            CapteurDistance(sensor_sample_count=5, sensor_sample_delay=0, max_distance=4.0)
    
    def test_with_sample_count_as_very_high(self):
        with self.assertRaises(ValueError):
            CapteurDistance(sensor_sample_count=1000000, sensor_sample_delay=0.01, max_distance=4.0)
    
    def test_with_sample_delay_as_very_high(self):
        with self.assertRaises(ValueError):
            CapteurDistance(sensor_sample_count=5, sensor_sample_delay=1000000, max_distance=4.0)
    
    def test_with_max_distance_as_zero(self):
        with self.assertRaises(ValueError):
            CapteurDistance(sensor_sample_count=5, sensor_sample_delay=0.01, max_distance=0)

    
        
if __name__ == '__main__':
    unittest.main()