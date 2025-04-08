import time
import pigpio

from .i_sensor import i_sensor

#INA219 register addresses
CONFIG_REG      = 0x00
SHUNT_VOLT_REG  = 0x01
BUS_VOLT_REG    = 0x02
POWER_REG       = 0x03
CURRENT_REG     = 0x04
CALIBRATION_REG = 0x05

class VoltageSensor(i_sensor):
    """
    Class for RGB sensor that check the voltage

    This class uses pigpio for I2C communication

    @param name: Optional sensor name
    @param address: I2C address of the INA219 (default 0x40)
    @param bus: I2C bus number (default 1)
    @param r_shunt: The value (in ohms) of shunt resistor.
    @param max_current: Maximum expected current (in A) of measurement system
    @param bus_voltage_range: Maximum bus voltage range. For a 5V system, we must use 16
    """

    def __init__(self, name: str="", address: int = 0x40, bus: int = 1, r_shunt: float = 0.1, max_current: float = 3.2, bus_voltage_range: int = 16):
        """Constructor of voltage_sensor"""

        self._name = name
        self._r_shunt = r_shunt
        self._max_current = max_current

        if bus_voltage_range not in (16, 32):
            raise ValueError("Unsupported bus voltage range. Choose either 16 or 32 V")
        self._bus_voltage_range = bus_voltage_range
        
        #initialize the pigpio instance and open the I2C handle
        self._pi = pigpio.pi()
        if not self._pi.connected:
            raise IOError("Could not connect to pigpio daemon")

        #address by default is 0x40 for i2c connection
        self._handle = self._pi.i2c_open(bus, address)

        self._calibrate_sensor()


    def _calibrate_sensor(self):
        """Configure and calibrate the INA219 using the formula in the datasheet
        
        :raises IOError: Error if register fails to write data
        """

        self._current_lsb = self._max_current / 32768.0  # [A/bit]
        
        # Compute the calibration register value using the datasheet formula.
        calibration_value = int(0.04096 / (self._current_lsb * self._r_shunt))
        
        # Write the calibration value to the calibration register.
        status = self._pi.i2c_write_word_data(self._handle, CALIBRATION_REG, calibration_value)
        if status < 0:
            raise IOError("Failed to write calibration register")
        
        # configuration for 16V
        if self._bus_voltage_range == 16:
            configuration = 0x199F 
        # configuration for 32V
        elif self._bus_voltage_range == 32:
            configuration = 0x499F
             
        status = self._pi.i2c_write_word_data(self._handle, CONFIG_REG, configuration)
        if status < 0:
            raise IOError("Failed to write configuration register")
        
    def _read_bytes(self, register):
        """Reads data in bytes from the sensor. 8 lowest bits are used
        
        :raises IOError: Error if register can't be read
        """

        count, data = self._pi.i2c_read_word_data(self._handle, register)
        if count != 2:
            raise IOError(f"Failed to read register 0x{register:02X}")
        
        #bit swap in 8 to ensure the usage of only the lower 8 bits from the shifted value
        swapped = ((data & 0xFF) << 8) | ((data >> 8) & 0xFF)
        return swapped


    def read_data(self):
        """Displays data after treating"""

        raw_bus = self._read_bytes(BUS_VOLT_REG)
        bus_voltage_mv = (raw_bus >> 3) * 4  #each LSB equals 4 mV.
        bus_voltage = bus_voltage_mv / 1000.0
        
        raw_current = self._read_bytes(CURRENT_REG)
        #convert from two's complement if necessary for extra security
        if raw_current & 0x8000:
            raw_current -= 65536
        current_A = raw_current * self._current_lsb  #convert to A using the formula
        current_mA = current_A * 1000.0
        
        return {
            "bus_voltage": bus_voltage,
            "current": current_mA
        }
    
    def display_data(self):
        """Display current data"""

        data = self.read_data()
        print(f"INA219 Sensor ({self._name}): Bus Voltage = {data['bus_voltage']:.2f} V, "
              f"Current = {data['current']:.2f} mA")


    def close(self):
        """Closes the I2C connection and stops the pigpio instance
        
        :raises IOError: Error while closing i2c connection
        """

        try:
            self._pi.i2c_close(self._handle)
            self._pi.stop()
        except Exception as e:
            raise IOError("Failed to close INA219 sensor properly: " + str(e))
