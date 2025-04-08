from .i_sensor import i_sensor

class VoltageSensor(i_sensor):
    """
    Class for RGB sensor that check the voltage

    @param name: name of the component (str)
    @param pins: list of pins used by the component (list<int>)
    @param voltage: voltage used by the component (float)
    @param I2C_ADDRESS: constant for the i2c protocol pin
    """

    I2C_ADDRESS = 0x00

    def __init__(self, name: str="", pins: list=..., voltage: float=0.0):

        super().__init__(name, pins, voltage)
        self._color = None

    def read_data(self):
        """Reads data from the sensor"""
        pass

    def display_data(self):
        """Displays data after treating"""
        pass

    def get_voltage(self):
        """Measures the current voltage"""
        pass
