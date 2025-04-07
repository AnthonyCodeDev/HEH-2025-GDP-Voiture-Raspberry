import pigpio

from composants.ISensor import ISensor

COMMAND_BIT = 0x80
ENABLE      = 0x00
ATIME       = 0x01
CONTROL     = 0x0F
CDATAL      = 0x14  # Clear data low byte; high byte is CDATAH = 0x15
RDATAL      = 0x16  # Red data low byte; high byte is RDATAH = 0x17
GDATAL      = 0x18  # Green data low byte; high byte is GDATAH = 0x19
BDATAL      = 0x1A  # Blue data low byte; high byte is BDATAH = 0x1B

class RgbSensor(ISensor):
    """
    Class for RGB sensor that detects colors, needed to check the departure light (green)

    Uses pigpio for i2c connection

    @param name: name of the component (str)
    @param pins: list of pins used by the component (list<int>)
    @param color: color detected, transformed into readable format using a range of colors (str)
    """

    def __init__(self, name: str="", pins: list=..., address = 0x29, bus=1):

        self._name = name
        self._color = None

        #pigpio daemon
        self._pi = pigpio.pi()
        if not self.pi.connected:
            raise IOError("Could not connect to pigpio daemon")
        # Open an I2C connection on the specified bus and address
        self.handle = self.pi.i2c_open(bus, address)
        self._initialize_sensor()
        

    def _initialize_sensor(self):
        # Power on the sensor by writing to the ENABLE register.
        # For TCS34725, writing 0x03 to ENABLE turns on the oscillator and enables the sensor.
        self.bus.write_byte_data(self.address, COMMAND_BIT | ENABLE, 0x03)
        # Set integration time (e.g., 0xD5) and gain (e.g., 0x01) as needed.
        self.bus.write_byte_data(self.address, COMMAND_BIT | ATIME, 0xD5)
        self.bus.write_byte_data(self.address, COMMAND_BIT | CONTROL, 0x01)

    def _read_word(self, register):
        """Reads a word (two bytes) from the specified register."""
        low = self.bus.read_byte_data(self.address, COMMAND_BIT | register)
        high = self.bus.read_byte_data(self.address, COMMAND_BIT | (register + 1))
        return (high << 8) | low
    
    def read_data(self):
        """Reads 3 bytes for colors, transforms them into integers and defines the color based on a range of color"""
         
        red   = int.from_bytes(self._read_word(RDATAL))
        green = int.from_bytes(self._read_word(GDATAL))
        blue  = int.from_bytes(self._read_word(BDATAL))

        if (red > green + blue):
            return "RED"
        elif (green > red + blue):
            return "GREEN"
        elif (blue > green + red):
            return "BLUE"
        else:
            return "NOT_DEFINED"


    def display_data(self):
        """Displays data after treating"""

        self._color = self.read_data()
        pass
