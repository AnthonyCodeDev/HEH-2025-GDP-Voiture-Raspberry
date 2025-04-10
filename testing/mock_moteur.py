#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os

class TestMotorController(unittest.TestCase):
    @patch.dict('sys.modules', {'RPi': MagicMock(), 'RPi.GPIO': MagicMock(), 'PCA': MagicMock(), 'PWM': MagicMock()})
    def setUp(self):
        # Ajouter le chemin parent à sys.path
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Importer après avoir mocké les modules
        from projet_voiture.ControllerMotor import ControllerMotor
        self.ControllerMotor = ControllerMotor
        
        # Créer une instance du contrôleur
        self.controller = self.ControllerMotor()

    def test_forward(self):
        self.controller.forward(100)
        self.controller._ControllerMotor__pwm_controller.write.assert_any_call(4, 0, 4095)
        self.controller._ControllerMotor__pwm_controller.write.assert_any_call(5, 0, 4095)

    def test_backward(self):
        self.controller.backward(-100)
        self.controller._ControllerMotor__pwm_controller.write.assert_any_call(4, 0, 4095)
        self.controller._ControllerMotor__pwm_controller.write.assert_any_call(5, 0, 4095)

    def test_stop(self):
        self.controller.stop()
        self.controller._ControllerMotor__pwm_controller.write.assert_any_call(4, 0, 0)
        self.controller._ControllerMotor__pwm_controller.write.assert_any_call(5, 0, 0)

    def test_backward_invalid_speed(self):
        with self.assertRaises(ValueError):
            self.controller.backward(50)

if __name__ == '__main__':
    unittest.main()