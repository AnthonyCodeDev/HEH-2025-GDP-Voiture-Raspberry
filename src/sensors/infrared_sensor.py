#Created by Wiktor Chabowski
#07-04-2024
#Part of nano-computers project

from gpiozero import DigitalInputDevice

from .i_sensor import i_sensor

class infrared_sensor(i_sensor):
    """
    Class for infrared sensor needed to check the black arrival line. The car stops when black is detected, else it continues

    @param name: name of the component (str)
    @param pin: pin used by the component (int)
    @param state: state for white - False and black - True (bool)
    """

    def __init__(self, name: str="", pin: int=0):
        """Constructor of the infrared sensor, initializing with name, pins voltage and state (False by default)
        Assumes pull_up=True and active_state=True 
        """

        self._digitalDevice = DigitalInputDevice(pin=pin, pull_up=True, active_state=True)
        self._name = name
        self._state = False

    def read_data(self):
        """Reads data from the sensor
        
        :raises Exception: Error while reading data from sensor
        """

        try:
            value = self._digitalDevice.value
            self._state = value
            return self._state
        except Exception as e:
            raise Exception(f"Error reading infrared sensor data: {e}")

    def display_data(self):
        """Displays the current :attr:`_state`
        
        :raises Exception: Error while displaying data
        """

        try:
            #Appel de log listener si implémenté
            data = self.read_data()
            if data:
                print("BLACK")
            else:
                print("WHITE")
        except Exception as e:
            print(f"Error displaying sensor data: {e}")

    def change_state(self):
        """Change the  :attr:`_state` of white/black"""

        self._state = not self._state