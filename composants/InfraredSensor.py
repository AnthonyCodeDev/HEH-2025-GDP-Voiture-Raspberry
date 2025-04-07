from gpiozero import DigitalInputDevice

from composants.ISensor import ISensor

class InfraredSensor(DigitalInputDevice, ISensor):
    """
    Class for infrared sensor needed to check the black arrival line. The car stops when black is detected, else it continues

    @param name: name of the component (str)
    @param pin: pin used by the component (int)
    @param state: state for white - False and black - True (bool)
    """

    def __init__(self, name: str="", pin: int=0):
        """Constructor of the infrared sensor, initializing with name, pins voltage and state (False by default)"""

        DigitalInputDevice.__init__(pin, True, True, None, None)
        self._name = name
        self._state = False

    def read_data(self):
        """Reads data from the sensor"""
        pass

    def display_data(self):
        """Displays the current :attr:`_state`"""

        data = self.read_data()

        #Appel de log listener si implémenté
        if data:
            print("BLACK")
        else:
            print("WHITE")

    def change_state(self):
        """Change the  :attr:`_state` of white/black"""
        return not self._state