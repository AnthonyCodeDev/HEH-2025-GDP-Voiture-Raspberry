import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
from motors.dc_motor import DcMotor

class TestDcMotor(unittest.TestCase):

    @patch('motors.dc_motor.Motor')  # 👈 patch du bon chemin vers Motor dans ton fichier
    def setUp(self, mock_motor_class):
        self.mock_motor_instance = MagicMock()
        mock_motor_class.return_value = self.mock_motor_instance

        # Initialisation de DcMotor avec des broches factices
        self.dc_motor = DcMotor(forward=17, backward=18)

    def test_forward(self):
        self.dc_motor.forward()
        self.mock_motor_instance.forward.assert_called_once()

    def test_backward(self):
        self.dc_motor.backward()
        self.mock_motor_instance.backward.assert_called_once()

    def test_stop(self):
        self.dc_motor.stop()
        self.mock_motor_instance.stop.assert_called_once()

    def test_read_data(self):
        self.mock_motor_instance.is_active = True
        result = self.dc_motor.read_data()
        self.assertEqual(result, {'is_active': True})

    def test_display_data_running(self):
        self.mock_motor_instance.is_active = True
        with patch('builtins.print') as mock_print:
            self.dc_motor.display_data()
            mock_print.assert_called_with('Motor is running')

    def test_display_data_stopped(self):
        self.mock_motor_instance.is_active = False
        with patch('builtins.print') as mock_print:
            self.dc_motor.display_data()
            mock_print.assert_called_with('Motor is stopped')

if __name__ == '__main__':
    unittest.main()