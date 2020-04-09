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

class device:

    def __init__(self, i2cAddr=TSL2561_I2C_ADDR_DEFAULT,
            integrationTime=TSL2561_INTEGRATION_TIME_402, debug=False):

        self.i2cAddr = i2cAddr
        self.i2c = I2C(0, I2C.MASTER)
        self.debugOutput = debug
        self.integrationTime = TSL2561_INTEGRATION_TIME_402
        self.gain = TSL2561_GAIN_16X
        self.ready = False
        self.error = False

    def init(self):
        tslReg = None
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
            self.applyTiming()

    def enable(self):
        if not self.ready:
            return
        try:
            self.i2c.writeto_mem(self.i2cAddr, TSL2561_REG_CONTROL|TSL2561_CMD,
                0x03)
        except OSError:
            print('I2C Error')
            self.error = True

    def disable(self):
        if not self.ready:
            return
        try:
            self.i2c.writeto_mem(self.i2cAddr, TSL2561_REG_CONTROL|TSL2561_CMD,
                0x00)
        except OSError:
            print('I2C Error')
            self.error = True

    def applyTiming(self):
        self.enable()
        try:
            self.i2c.writeto_mem(self.i2cAddr, TSL2561_REG_TIMING|TSL2561_CMD,
                self.integrationTime + self.gain)
        except OSError:
            print('I2C Error')
            self.error = True
        self.disable()

    def setIntegrationTime(self, integrationTime):
        self.integrationTime = integrationTime
        applyTiming(self)

    def getSensorDataRaw(self):
        lumB = 0
        lumIR = 0

        if self.error == True:
            self.error = False
            self.applyTiming()

        self.enable()

        if self.integrationTime == TSL2561_INTEGRATION_TIME_13_7:
            utime.sleep_ms(15)
        elif self.integrationTime == TSL2561_INTEGRATION_TIME_101:
            utime.sleep_ms(120)
        else:
            utime.sleep_ms(450)

        tslReg = None;
        try:
            tslReg = self.i2c.readfrom_mem(self.i2cAddr,
                TSL2561_REG_ADC_B|TSL2561_CMD|TSL2561_WORD, 2)
        except OSError:
            print('I2C Error')
            self.error = True
        if tslReg is not None:
            lumB = (tslReg[1]<<8) + tslReg[0]

        tslReg = None;
        try:
            tslReg = self.i2c.readfrom_mem(self.i2cAddr,
                TSL2561_REG_ADC_IR|TSL2561_CMD|TSL2561_WORD, 2)
        except OSError:
            print('I2C Error')
            self.error = True
        if tslReg is not None:
            lumIR = (tslReg[1]<<8) + tslReg[0]

        self.disable()

        return {'lumB': lumB, 'lumIR': lumIR}

    def getSensorDataAGC(self):
        agcDone = False
        done = False

        while not done:
            lum = self.getSensorDataRaw()
            if lum is None:
                return None

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
                    self.gain = TSL2561_GAIN_16X
                    self.applyTiming()
                    agcDone = True
                elif lum['lumB'] > thHigh and self.gain == TSL2561_GAIN_16X:
                    self.gain = TSL2561_GAIN_1X
                    self.applyTiming()
                    agcDone = True
                else:
                    agcDone = True
                    done = True
            else:
                done = True
        if self.debugOutput == True:
            print('Final Broadband: ' + str(lum['lumB']))
            print('Final IR: ' + str(lum['lumIR']))
        return lum

    def getLux(self):
        lum = self.getSensorDataAGC()
        if lum is None:
            return None

        if self.integrationTime == TSL2561_INTEGRATION_TIME_13_7:
            clipThreshold = 4900
            scale = 0x7517
        elif self.integrationTime == TSL2561_INTEGRATION_TIME_101:
            clipThreshold = 37000
            scale = 0x0FE7
        else:
            clipThreshold = 65000
            scale = 1024 # 2^10

        if lum['lumB'] >= clipThreshold or lum['lumIR'] >= clipThreshold:
            return None

        if self.gain == TSL2561_GAIN_1X:
            if self.debugOutput == True:
                print('Gain: 1x')
            scale = scale * 16
        else:
            if self.debugOutput == True:
                print('Gain: 16x')

        channel0 = (lum['lumB'] * scale) >> 10
        channel1 = (lum['lumIR'] * scale) >> 10

        ratio1 = 0
        if channel0 != 0:
            ratio1 = (channel1 << 10) / channel0

        ratio = int((ratio1 + 1)) >> 1;

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
