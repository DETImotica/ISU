# TSL2561 driver for MicroPython on ESP32
# MIT license; Copyright (c) 2018 Philipp Bolte (philipp@bolte.engineer)
# Version 0.1 beta (2018/09/10)

""" TSL2561 driver module for the WiPy 3 board

This module provides a driver for the TSL2561 luminosity sensor using an
I2C interface. It includes the conversion of the raw sensor data to a value
given in Lux. The proposed method included in the devices datasheet was used
for the measurement conversion. Also a simple AGC is included to switch
the gain of the sensor between 1x and 16x. The AGC was inspired by the
Adafruit TSL2561 library for Arduino.
The module was designed for the pycom WiPy 3 module.

Example:
    The TSL2561 driver can be used as follows:

    .. code-block:: html
        :linenos:

        tslDev = TSL2561.device()
        tslDev.init()
        lux = tslDev.getLux()

"""

import utime
from machine import I2C

# Default I2C address that is used
TSL2561_I2C_ADDR_DEFAULT = 0x39
"""Default TSL2561 I2C slave address"""

# Register map of the TSL2561 sensor
TSL2561_CMD = 0x80
TSL2561_WORD = 0x20
TSL2561_REG_CONTROL = 0x00
TSL2561_REG_TIMING = 0x01
TSL2561_REG_ID = 0x0A
TSL2561_REG_ADC_B = 0x0C
TSL2561_REG_ADC_IR = 0x0E

# Constants for the available integration times
TSL2561_INTEGRATION_TIME_13_7 = 0
"""Integration time of 13.7 ms"""

TSL2561_INTEGRATION_TIME_101 = 1
"""Integration time of 101 ms"""

TSL2561_INTEGRATION_TIME_402 = 0
"""Integration time of 402 ms"""

# Constants for the available gain stages
TSL2561_GAIN_1X = 0
TSL2561_GAIN_16X = 1<<4

# Constants used for the optimzed calculation of the luminosity in Lux
# See datasheet for details
TSL2561_LUX_K1T = (0x0040)
TSL2561_LUX_B1T = (0x01f2)
TSL2561_LUX_M1T = (0x01be)
TSL2561_LUX_K2T = (0x0080)
TSL2561_LUX_B2T = (0x0214)
TSL2561_LUX_M2T = (0x02d1)
TSL2561_LUX_K3T = (0x00c0)
TSL2561_LUX_B3T = (0x023f)
TSL2561_LUX_M3T = (0x037b)
TSL2561_LUX_K4T = (0x0100)
TSL2561_LUX_B4T = (0x0270)
TSL2561_LUX_M4T = (0x03fe)
TSL2561_LUX_K5T = (0x0138)
TSL2561_LUX_B5T = (0x016f)
TSL2561_LUX_M5T = (0x01fc)
TSL2561_LUX_K6T = (0x019a)
TSL2561_LUX_B6T = (0x00d2)
TSL2561_LUX_M6T = (0x00fb)
TSL2561_LUX_K7T = (0x029a)
TSL2561_LUX_B7T = (0x0018)
TSL2561_LUX_M7T = (0x0012)
TSL2561_LUX_K8T = (0x029a)
TSL2561_LUX_B8T = (0x0000)
TSL2561_LUX_M8T = (0x0000)

# Class for interfacing the TSL2561 sensor
class device:
    """Represents the TSL2561 device.

    Args:
        i2cAddr (int, optional): TSL2561 slave I2C address
        integrationTime (int, optional): Integration time
            (Please use available constants)
        debug (bool, optional): Debug information is printed when set to
            true

    """

    # Constructor
    # Used to initialize the internal data structure of the class
    def __init__(self, i2cAddr=TSL2561_I2C_ADDR_DEFAULT,
            integrationTime=TSL2561_INTEGRATION_TIME_402, debug=False):

        self.i2cAddr = i2cAddr
        self.i2c = I2C(0, I2C.MASTER)
        self.debugOutput = debug
        self.integrationTime = TSL2561_INTEGRATION_TIME_402
        self.gain = TSL2561_GAIN_16X
        self.ready = False
        self.error = False

    # Initialize the sensor
    def init(self):
        """ Initialize the sensor.

        Read the sensor ID register to check for valid device ID and
        set the timing and gain register.

        """
        tslReg = None
        # Try to read the device ID register
        try:
            tslReg = self.i2c.readfrom_mem(self.i2cAddr, TSL2561_REG_ID, 1)
        except OSError:
            print("TSL2561: I2C Error")
        if tslReg is not None:
            self.ready = True
            if self.debugOutput == True:
                if (tslReg[0] >> 8) == 0:
                    print('Found TSL2560! Revision: ' + str(tslReg[0] & 0x0F))
                elif (tslReg[0] >> 8) == 1:
                    print('Found TSL2561! Revision: ' + str(tslReg[0] & 0x0F))
        else:
            self.ready = False
            if self.debugOutput == True:
                print('No TSL2560/1 sensor found!')

        if self.ready == True:
            # Set default integration time and gain
            self.applyTiming()

    # Power up the device
    def enable(self):
        if not self.ready:
            return
        try:
            self.i2c.writeto_mem(self.i2cAddr, TSL2561_REG_CONTROL|TSL2561_CMD,
                0x03)
        except OSError:
            print('I2C Error')
            self.error = True

    # Power down the device
    def disable(self):
        if not self.ready:
            return
        try:
            self.i2c.writeto_mem(self.i2cAddr, TSL2561_REG_CONTROL|TSL2561_CMD,
                0x00)
        except OSError:
            print('I2C Error')
            self.error = True

    # Apply the integration time and gain
    def applyTiming(self):
        self.enable()
        try:
            self.i2c.writeto_mem(self.i2cAddr, TSL2561_REG_TIMING|TSL2561_CMD,
                self.integrationTime + self.gain)
        except OSError:
            print('I2C Error')
            self.error = True
        self.disable()

    # Set the integration time
    def setIntegrationTime(self, integrationTime):
        """Update the integration time

        Args:
            integrationTime (int, optional): Integration time
                (Please use available constants)

        """
        self.integrationTime = integrationTime
        applyTiming(self)

    # Read the raw values for broadband and IR luminosity
    def getSensorDataRaw(self):
        """Starts a measurement and returns the measured raw values

        Returns:
            dictionary{'lumB', 'lumIR'}, []:

            Returns a dictionary with the raw sensor values
            or an empty object in case of measurement error

        Example:
            .. code-block:: html
                :linenos:

                raw = lum.getSensorDataRaw()
                if raw is not None:
                    print('B:' + raw['lumB'])
                    print('IR:' + raw['lumIR'])

        """
        lumB = 0
        lumIR = 0

        # Reset timing in case of previous I2C error
        if self.error == True:
            self.error = False
            self.applyTiming()

        # Power up sensor
        self.enable()

        # Wait for conversion to be done
        if self.integrationTime == TSL2561_INTEGRATION_TIME_13_7:
            utime.sleep_ms(15)
        elif self.integrationTime == TSL2561_INTEGRATION_TIME_101:
            utime.sleep_ms(120)
        else: # TSL2561_INTEGRATION_TIME_402
            utime.sleep_ms(450)

        # Read the value of the broadband luminosity ADC register
        tslReg = None;
        try:
            tslReg = self.i2c.readfrom_mem(self.i2cAddr,
                TSL2561_REG_ADC_B|TSL2561_CMD|TSL2561_WORD, 2)
        except OSError:
            print('I2C Error')
            self.error = True
        if tslReg is not None:
            lumB = (tslReg[1]<<8) + tslReg[0]

        # Read the value of the IR luminosity ADC register
        tslReg = None;
        try:
            tslReg = self.i2c.readfrom_mem(self.i2cAddr,
                TSL2561_REG_ADC_IR|TSL2561_CMD|TSL2561_WORD, 2)
        except OSError:
            print('I2C Error')
            self.error = True
        if tslReg is not None:
            lumIR = (tslReg[1]<<8) + tslReg[0]

        # Power down the sensor
        self.disable()

        return {'lumB': lumB, 'lumIR': lumIR}

    # Read the raw sensor values and change gain if required
    def getSensorDataAGC(self):
        """Starts a measurement with AGC and returns the measured raw values

        Returns:
            dictionary{'lumB', 'lumIR'}, []:

            Returns a dictionary with the raw sensor values
            or an empty object in case of measurement error

        Example:
            .. code-block:: html
                :linenos:

                raw = lum.getSensorDataAGC()
                if raw is not None:
                    print('B:' + raw['lumB'])
                    print('IR:' + raw['lumIR'])

        """

        # Automatic Gain Control done flag
        agcDone = False

        # Measurement Done flag
        done = False

        # Measure until the luminosity value is in a valid range
        while not done:
            # Get raw data
            lum = self.getSensorDataRaw()
            if lum is None:
                return None

            # Set threholds for Gain Control depending on integration time
            if self.integrationTime == TSL2561_INTEGRATION_TIME_13_7:
                thLow = 100
                thHigh = 4850
            elif self.integrationTime == TSL2561_INTEGRATION_TIME_101:
                thLow = 200
                thHigh = 36000
            else:
                thLow = 500
                thHigh = 63000

            if not agcDone:
                if lum['lumB'] < thLow and self.gain == TSL2561_GAIN_1X:
                    # Switch gain to 16x if in 1x and lum to low
                    self.gain = TSL2561_GAIN_16X
                    self.applyTiming()
                    agcDone = True
                elif lum['lumB'] > thHigh and self.gain == TSL2561_GAIN_16X:
                    # Switch to 1x if in 16x and lum to high
                    self.gain = TSL2561_GAIN_1X
                    self.applyTiming()
                    agcDone = True
                else:
                    # Gain stage is appropriate
                    agcDone = True
                    done = True
            else:
                # Gain was already switched in the last iteration
                # Use the current measurement for Lux calculation
                done = True
        if self.debugOutput == True:
            print('Final Broadband: ' + str(lum['lumB']))
            print('Final IR: ' + str(lum['lumIR']))
        return lum

    # Get sensor data with AGC and calculate resulting luminosity in Lux
    def getLux(self):
        """Starts a measurement with AGC and returns the luminosity in Lux

        Returns:
            int, []:

            Returns the measured luminosity in Lux
            or an empty object in case of measurement error

        Example:
            .. code-block:: html
                :linenos:

                raw = lum.getLux()
                if raw is not None:
                    print('Lux:' + raw)

        """

        # Get raw sensor data and switch gain if required
        lum = self.getSensorDataAGC()
        if lum is None:
            return None

        # The calculation of the luminosity in Lux is based on the datasheet
        # of the TSL2561 sensor. It is optimized for fast execution rather then
        # a good code readability.

        # Select clipping threshold and scale based on integration time
        if self.integrationTime == TSL2561_INTEGRATION_TIME_13_7:
            clipThreshold = 4900
            scale = 0x7517
        elif self.integrationTime == TSL2561_INTEGRATION_TIME_101:
            clipThreshold = 37000
            scale = 0x0FE7
        else:
            clipThreshold = 65000
            scale = 1024 # 2^10

        # Return 0 in case of clipping (sensor value out of range)
        if lum['lumB'] >= clipThreshold or lum['lumIR'] >= clipThreshold:
            return None

        # Increase scale if gain is 1x
        if self.gain == TSL2561_GAIN_1X:
            if self.debugOutput == True:
                print('Gain: 1x')
            scale = scale * 16
        else:
            if self.debugOutput == True:
                print('Gain: 16x')

        channel0 = (lum['lumB'] * scale) >> 10
        channel1 = (lum['lumIR'] * scale) >> 10

        # ration B / IR
        ratio1 = 0
        if channel0 != 0:
            ratio1 = (channel1 << 10) / channel0

        ratio = int((ratio1 + 1)) >> 1;

        # only valid for non chipscale
        if ratio >= 0 and ratio < TSL2561_LUX_K1T:
            b = TSL2561_LUX_B1T
            m = TSL2561_LUX_M1T
        elif ratio <= TSL2561_LUX_K2T:
            b = TSL2561_LUX_B2T
            m = TSL2561_LUX_M2T
        elif ratio <= TSL2561_LUX_K3T:
            b = TSL2561_LUX_B3T
            m = TSL2561_LUX_M3T
        elif ratio <= TSL2561_LUX_K4T:
            b = TSL2561_LUX_B4T
            m = TSL2561_LUX_M4T
        elif ratio <= TSL2561_LUX_K5T:
            b = TSL2561_LUX_B5T
            m = TSL2561_LUX_M5T
        elif ratio <= TSL2561_LUX_K6T:
            b = TSL2561_LUX_B6T
            m = TSL2561_LUX_M6T
        elif ratio <= TSL2561_LUX_K7T:
            b = TSL2561_LUX_B7T
            m = TSL2561_LUX_M7T
        else:
            b = TSL2561_LUX_B8T
            m = TSL2561_LUX_M8T

        temp = ((channel0 * b) - (channel1 * m));
        if temp < 0:
            temp = 0

        temp += (1 << (13));

        lux = temp >> 14

        if self.debugOutput == True:
            print('Lux: ' + str(lux))

        return lux
