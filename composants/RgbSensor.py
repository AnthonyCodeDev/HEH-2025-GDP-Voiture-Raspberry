#Created by Wiktor Chabowski
#07-04-2024
#Part of nano-computers project

import pigpio

from ISensor import ISensor

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
    @param address: I2C address of the sensor (int)
    @param bus: I2C bus number (int
    """

    def __init__(self, name: str="", pins: list=..., address = 0x29, bus=1):

        self._name = name
        self._color = None
        self._pins = pins if pins is not None else []

        #pigpio daemon
        self._pi = pigpio.pi()
        if not self.pi.connected:
            raise IOError("Could not connect to pigpio daemon")
        # Open an I2C connection on the specified bus and address
        self.handle = self.pi.i2c_open(bus, address)
        self._initialize_sensor()
        

    def _initialize_sensor(self):
        """Initiallize ENABLE, ATIME and CONTROL registers
        ENABLE: 0x03 activates the sensor
        ATIME: 0xD5 determines integration time 
        CONTROL: 0x01 sets the gain to amplify light signal

        :raises IOError: Error while putting values into specific register
        """

        # Power on the sensor by writing to the ENABLE register.
        # For TCS34725, writing 0x03 to ENABLE turns on the oscillator and enables the sensor.
        try:
            ret = self._pi.i2c_write_byte_data(self._handle, COMMAND_BIT | ENABLE, 0x03)
            if ret < 0:
                raise IOError("Failed to write to ENABLE register")
            ret = self._pi.i2c_write_byte_data(self._handle, COMMAND_BIT | ATIME, 0xD5)
            if ret < 0:
                raise IOError("Failed to write to ATIME register")
            ret = self._pi.i2c_write_byte_data(self._handle, COMMAND_BIT | CONTROL, 0x01)
            if ret < 0:
                raise IOError("Failed to write to CONTROL register")
        except Exception as e:
            raise IOError(f"Error initializing RGB sensor: {e}")
        
    def read_byte(self, register: int):
        """Reads a single byte from the specified register

        :raises IOError: Error while reading byte from a specific register
        """

        try:
            count, data = self._pi.i2c_read_byte_data(self._handle, COMMAND_BIT | register)
            if count != 1:
                raise IOError(f"Failed to read byte from register 0x{register:02X}")
            return data
        except Exception as e:
            raise IOError(f"Error reading byte from register 0x{register:02X}: {e}")

    def _read_word(self, register):
        """Reads a word (two bytes) from the specified register."""

        low = self.read_byte(register)
        high = self.read_byte(register + 1)
        return (high << 8) | low
    
    def read_data(self):
        """Reads 3 bytes for colors, transforms them into integers and defines the color based on a range of color
        
        :raises IOError: Error while reading data from sensor
        """

        try:
            red = self._read_word(RDATAL)
            green = self._read_word(GDATAL)
            blue = self._read_word(BDATAL)

            if red > green + blue and red > 130:
                self._color = "RED"
            elif green > red + blue and green > 130:
                self._color = "GREEN"
            elif blue > red + green and blue > 130:
                self._color = "BLUE"
            else:
                self._color = "NOT_DEFINED"
            return self._color
        except Exception as e:
            raise IOError(f"Error reading RGB sensor data: {e}")


    def display_data(self):
        """Displays data after treating
        
        :raises Exception: Error while displaying sensor data
        """

        try:
            color = self.read_data()
            print(f"Detected Color: {color}")
        except Exception as e:
            print(f"Error displaying RGB sensor data: {e}")

    def close(self):
        """Closes the I2C connection and the pigpio instance
        
        :raises IOError: Error while closing i2c connection
        """

        try:
            self._pi.i2c_close(self._handle)
            self._pi.stop()
        except Exception as e:
            raise IOError(f"Error closing RGB sensor: {e}")
