import unittest
from unittest.mock import patch, MagicMock
import capteur_ultra_son

class TestCapteurUltrason(unittest.TestCase):

    @patch('capteur_ultra_son.DistanceSensor')
    def test_auto_check_distance_valide(self, mock_sensor_class):
        """✅ Capteur retourne une distance correcte (ex : 25 cm)"""
        mock_sensor = MagicMock()
        mock_sensor.distance = 0.25  # 25 cm
        mock_sensor_class.return_value = mock_sensor

        try:
            capteur_ultra_son.auto_check(mock_sensor)
        except SystemExit:
            self.fail("auto_check() a levé SystemExit malgré une distance valide")

    @patch('capteur_ultra_son.DistanceSensor')
    def test_auto_check_distance_trop_loin(self, mock_sensor_class):
        """❌ Distance > 400 cm"""
        mock_sensor = MagicMock()
        mock_sensor.distance = 5.0  # 500 cm
        mock_sensor_class.return_value = mock_sensor

        with self.assertRaises(SystemExit):
            capteur_ultra_son.auto_check(mock_sensor)

    @patch('capteur_ultra_son.DistanceSensor')
    def test_auto_check_distance_trop_proche(self, mock_sensor_class):
        """❌ Distance < 2 cm"""
        mock_sensor = MagicMock()
        mock_sensor.distance = 0.01  # 1 cm
        mock_sensor_class.return_value = mock_sensor

        with self.assertRaises(SystemExit):
            capteur_ultra_son.auto_check(mock_sensor)

    @patch('capteur_ultra_son.DistanceSensor')
    def test_auto_check_distance_aberrante(self, mock_sensor_class):
        """❌ Distance > 10 mètres"""
        mock_sensor = MagicMock()
        mock_sensor.distance = 12.0  # 1200 cm
        mock_sensor_class.return_value = mock_sensor

        with self.assertRaises(SystemExit):
            capteur_ultra_son.auto_check(mock_sensor)

    @patch('capteur_ultra_son.DistanceSensor')
    def test_auto_check_distance_negative(self, mock_sensor_class):
        """❌ Valeur négative"""
        mock_sensor = MagicMock()
        mock_sensor.distance = -1.0
        mock_sensor_class.return_value = mock_sensor

        with self.assertRaises(SystemExit):
            capteur_ultra_son.auto_check(mock_sensor)

    @patch('capteur_ultra_son.DistanceSensor')
    def test_auto_check_distance_null(self, mock_sensor_class):
        """❌ Capteur inactif (distance = 0)"""
        mock_sensor = MagicMock()
        mock_sensor.distance = 0.0
        mock_sensor_class.return_value = mock_sensor

        with self.assertRaises(SystemExit):
            capteur_ultra_son.auto_check(mock_sensor)

    @patch('capteur_ultra_son.DistanceSensor')
    def test_auto_check_distance_none(self, mock_sensor_class):
        """❌ Capteur renvoie None"""
        mock_sensor = MagicMock()
        mock_sensor.distance = None
        mock_sensor_class.return_value = mock_sensor

        with self.assertRaises(TypeError):
            capteur_ultra_son.auto_check(mock_sensor)

if __name__ == '__main__':
    unittest.main()
