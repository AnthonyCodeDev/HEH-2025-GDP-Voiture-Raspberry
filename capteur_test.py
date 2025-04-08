import unittest
from unittest.mock import patch, MagicMock
import capteur_ultra_son  # Ton script existant

class TestCapteurUltrason(unittest.TestCase):
    @patch('capteur_ultra_son.DistanceSensor')
    def test_auto_check_distance_valide(self, mock_sensor_class):
        """Test si le capteur retourne une distance valide"""
        mock_sensor = MagicMock()
        mock_sensor.distance = 0.25  # 25 cm
        mock_sensor_class.return_value = mock_sensor

        try:
            capteur_ultra_son.auto_check(mock_sensor)
        except SystemExit:
            self.fail("auto_check() a levé SystemExit malgré une distance valide")

    @patch('capteur_ultra_son.DistanceSensor')
    def test_auto_check_distance_trop_loin(self, mock_sensor_class):
        """Test si le capteur détecte une distance hors plage (trop loin)"""
        mock_sensor = MagicMock()
        mock_sensor.distance = 5.0  # 500 cm
        mock_sensor_class.return_value = mock_sensor

        with self.assertRaises(SystemExit):
            capteur_ultra_son.auto_check(mock_sensor)

    @patch('capteur_ultra_son.DistanceSensor')
    def test_auto_check_capteur_non_detecte(self, mock_sensor_class):
        """Test si le capteur lève une erreur si non connecté"""
        mock_sensor = MagicMock()
        mock_sensor.distance = 0.0  # Pas de signal
        mock_sensor_class.return_value = mock_sensor

        with self.assertRaises(SystemExit):
            capteur_ultra_son.auto_check(mock_sensor)

if __name__ == '__main__':
    unittest.main()
