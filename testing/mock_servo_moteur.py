#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock, patch
import sys
sys.modules['PWM'] = MagicMock()
from projet_voiture.ControllerServo import ControllerServo

class TestServoController(unittest.TestCase):
    def setUp(self):
        """
        Patch le constructeur de PWM dans le module servo_controller pour éviter l'accès réel au matériel.
        Toutes les instances de PWM créées dans ServoController seront remplacées par un objet fictif.
        """
        patcher = patch('projet_voiture.ControllerServo.PCA.PWM')
        self.addCleanup(patcher.stop)
        self.mock_pwm_class = patcher.start()
        self.mock_pwm_instance = MagicMock()
        self.mock_pwm_class.return_value = self.mock_pwm_instance
        self.servo = ControllerServo()

    def test_initialization(self):
        """Test l'initialisation du contrôleur et la configuration de la fréquence PWM."""
       
        # Vérification des paramètres par défaut
        self.assertEqual(self.servo.center_val, 320)
        self.assertEqual(self.servo.min_val, 200)
        self.assertEqual(self.servo.max_val, 500)
        # Vérifie que la fréquence a été définie sur 60Hz
        self.assertEqual(self.servo.pwm.frequency, 60)

    def test_rotate_positive_angles(self):
        """Test de la méthode rotate pour des angles positifs (et gestion du clamp)."""
        # On définit quelques cas de test sous forme de tuples (angle fourni, PWM attendue)
        test_cases = [
            (0, 320),
            (25, 320 + int((25 / 50.0) * (500 - 320))),  # 320 + (0.5 * 180) = 410
            (50, 500),
            (60, 500)  # 60 dépasse la limite, doit être clamped à 50° → PWM = 500
        ]
        
        for angle, expected_pwm in test_cases:
            self.servo.rotate(angle)
            # On récupère les arguments du dernier appel à pwm.write et on vérifie qu'ils correspondent
            self.assertEqual(self.mock_pwm_instance.write.call_args[0], (0, 0, expected_pwm))

    def test_rotate_negative_angles(self):
        """Test de la méthode rotate pour des angles négatifs (et gestion du clamp)."""

        test_cases = [
            (-25, 320 + int((-25 / 50.0) * (320 - 200))),  # 320 + (-0.5 * 120) = 260
            (-50, 200),
            (-100, 200)  # -100 doit être clamped à -50 → PWM = 200
        ]
        for angle, expected_pwm in test_cases:
            self.servo.rotate(angle)
            self.assertEqual(self.mock_pwm_instance.write.call_args[0], (0, 0, expected_pwm))

    def test_setToDegree_valid(self):
        """Test de la méthode setToDegree avec des angles valides."""

        test_cases = [
            (0, 320 + int((0 / 180.0) * (500 - 200))),     # 320 + (0 * 300) = 320
            (90, 320 + int((90 / 180.0) * (500 - 200))),    # 320 + (0.5 * 300) = 470
            (180, 320 + int((180 / 180.0) * (500 - 200)))   # 320 + (1 * 300) = 620
        ]
        for angle, expected_pwm in test_cases:
            self.servo.setToDegree(angle)
            self.assertEqual(self.mock_pwm_instance.write.call_args[0], (0, 0, expected_pwm))

    def test_setToDegree_invalid(self):
        """Test de la méthode setToDegree avec des angles hors limites (vérification du clamp)."""
        test_cases = [
            (-10, 320 + int((0 / 180.0) * (500 - 200))),    # -10 clamped à 0° → PWM = 320
            (200, 320 + int((180 / 180.0) * (500 - 200)))     # 200 clamped à 180° → PWM = 620
        ]
        for angle, expected_pwm in test_cases:
            self.servo.setToDegree(angle)
            self.assertEqual(self.mock_pwm_instance.write.call_args[0], (0, 0, expected_pwm))

    def test_resetRoue(self):
        """Test de la méthode resetRoue pour réinitialiser la roue à la position centrale."""

        self.servo.resetRoue()
        self.assertEqual(self.mock_pwm_instance.write.call_args[0], (0, 0, self.servo.center_val))

    def test_disable_pwm(self):
        """Test de la méthode disable_pwm pour s'assurer que la PWM est correctement désactivée."""

        self.servo.disable_pwm()
        self.assertEqual(self.mock_pwm_instance.write.call_args[0], (0, 0, 4096))

if __name__ == '__main__':
    unittest.main()