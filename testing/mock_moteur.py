#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock, call, patch
import sys
import os
from projet_voiture import ControllerMotor

# Ajoute le dossier parent au path pour pouvoir importer ControllerMotor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Projet voiture')))

class TestMotorController(unittest.TestCase):

    @patch('moteur.GPIO')
    @patch('moteur.PCA.PWM')
    def test_forward(self, mock_PWM, mock_GPIO):
        """
        Teste que la méthode forward envoie les bons signaux.
        Pour un forward(100), la valeur PWM calculée est 4095.
        """
        pwm_instance = MagicMock()
        mock_PWM.return_value = pwm_instance

        # Création de l'instance du contrôleur
        controller = ControllerMotor()

        # Réinitialisation des historiques de mocks
        mock_GPIO.output.reset_mock()
        pwm_instance.write.reset_mock()

        # Appel de la méthode forward
        controller.forward(100)

        # Pour un mouvement avant, on doit avoir :
        # Pour le moteur 0 (pins 17 et 18) : pin 17 à HIGH, 18 à LOW, canal d'activation 4
        # Pour le moteur 1 (pins 27 et 22) : pin 27 à HIGH, 22 à LOW, canal d'activation 5
        expected_gpio_calls = [
            call(17, mock_GPIO.HIGH),
            call(18, mock_GPIO.LOW),
            call(27, mock_GPIO.HIGH),
            call(22, mock_GPIO.LOW)
        ]
        mock_GPIO.output.assert_has_calls(expected_gpio_calls, any_order=True)

        expected_pwm_calls = [
            call(4, 0, 4095),
            call(5, 0, 4095)
        ]
        pwm_instance.write.assert_has_calls(expected_pwm_calls, any_order=True)

    @patch('moteur.GPIO')
    @patch('moteur.PCA.PWM')
    def test_backward(self, mock_PWM, mock_GPIO):
        """
        Teste que la méthode backward envoie les bons signaux.
        Pour un backward(-100), la valeur PWM calculée est -4095 (absolue 4095).
        """
        pwm_instance = MagicMock()
        mock_PWM.return_value = pwm_instance

        controller = ControllerMotor()
        mock_GPIO.output.reset_mock()
        pwm_instance.write.reset_mock()

        controller.backward(-100)

        # Pour un mouvement arrière, on attend :
        # Pour le moteur 0 (pins 17 et 18) : pin 17 à LOW, 18 à HIGH, canal 4
        # Pour le moteur 1 (pins 27 et 22) : pin 27 à LOW, 22 à HIGH, canal 5
        expected_gpio_calls = [
            call(17, mock_GPIO.LOW),
            call(18, mock_GPIO.HIGH),
            call(27, mock_GPIO.LOW),
            call(22, mock_GPIO.HIGH)
        ]
        mock_GPIO.output.assert_has_calls(expected_gpio_calls, any_order=True)

        expected_pwm_calls = [
            call(4, 0, 4095),
            call(5, 0, 4095)
        ]
        pwm_instance.write.assert_has_calls(expected_pwm_calls, any_order=True)

    @patch('moteur.GPIO')
    @patch('moteur.PCA.PWM')
    def test_stop(self, mock_PWM, mock_GPIO):
        """
        Teste la méthode stop qui doit envoyer une valeur 0.
        Pour stop(), la logique place les pins de commande à LOW (pour A) et HIGH (pour B).
        """
        pwm_instance = MagicMock()
        mock_PWM.return_value = pwm_instance

        controller = ControllerMotor()
        mock_GPIO.output.reset_mock()
        pwm_instance.write.reset_mock()

        controller.stop()

        # Pour stop, pwm_value est 0 :
        # Les sorties doivent être : pour chaque moteur, pin A en LOW, pin B en HIGH,
        # et l'écriture PWM doit être effectuée avec 0.
        expected_gpio_calls = [
            call(17, mock_GPIO.LOW),
            call(18, mock_GPIO.HIGH),
            call(27, mock_GPIO.LOW),
            call(22, mock_GPIO.HIGH)
        ]
        mock_GPIO.output.assert_has_calls(expected_gpio_calls, any_order=True)

        expected_pwm_calls = [
            call(4, 0, 0),
            call(5, 0, 0)
        ]
        pwm_instance.write.assert_has_calls(expected_pwm_calls, any_order=True)

    @patch('moteur.GPIO')
    @patch('moteur.PCA.PWM')
    def test_backward_invalid_speed(self, mock_PWM, mock_GPIO):
        """
        Teste que backward lève une exception lorsque la vitesse n'est pas négative.
        """
        pwm_instance = MagicMock()
        mock_PWM.return_value = pwm_instance

        controller = ControllerMotor()
        with self.assertRaises(ValueError):
            controller.backward(50)  # 50 est positif, doit lever ValueError.

    @patch('ControllerMotor.GPIO')
    @patch('ControllerMotor.PCA.PWM')
    def test_check_motor(self, mock_PWM, mock_GPIO):
        """
        Teste que check_motor envoie les bons signaux sur les broches moteur A/B sans activer PWM.
        """
        pwm_instance = MagicMock()
        mock_PWM.return_value = pwm_instance

        controller = ControllerMotor()  # instancie ton contrôleur

        # Nettoyer les historiques d'appels
        mock_GPIO.output.reset_mock() 

        # Appel de la méthode à tester
        result = controller.check_motor()

        # Vérifie que la méthode retourne True
        self.assertTrue(result)

        # Vérifie que chaque pin reçoit un HIGH suivi d’un LOW
        expected_calls = []
        for pin in [17, 18, 27, 22]:  # ordre basé sur __gpio_pins
            expected_calls.append(call(pin, mock_GPIO.HIGH))
            expected_calls.append(call(pin, mock_GPIO.LOW))

        mock_GPIO.output.assert_has_calls(expected_calls, any_order=False)

if __name__ == '__main__':
    unittest.main(defaultTest='TestMotorController.test_check_motor')
