from machine import I2C
from lib.bme680_constants import *
import math
import time

class BME680(BME680Data):
    def __init__(self, i2c_addr=0x77, i2c_device=None):
        BME680Data.__init__(self)

        self.i2c_addr = i2c_addr
        self._i2c = i2c_device

        self.chip_id = self._get_regs(0xd0, 1)
        if self.chip_id != 0x61:
            raise RuntimeError("BME680 Not Found. Invalid CHIP ID: 0x{0:02x}".format(self.chip_id))

        self.soft_reset()
        self.set_power_mode(0)

        self._get_calibration_data()

        self.set_humidity_oversample(2)
        self.set_pressure_oversample(3)
        self.set_temperature_oversample(4)
        self.set_filter(2)
        self.set_gas_status(0x01)

        self.get_sensor_data()

    def _get_calibration_data(self):
        calibration = self._get_regs(0x89, 25)
        calibration += self._get_regs(0xe1, 16)

        heat_range = self._get_regs(0x02, 1)
        heat_value = twos_comp(self._get_regs(0x00, 1), bits=8)
        sw_error = twos_comp(self._get_regs(0x04, 1), bits=8)

        self.calibration_data.set_from_array(calibration)
        self.calibration_data.set_other(heat_range, heat_value, sw_error)

    def soft_reset(self):
        self._set_regs(0xe0, 0xb6)
        time.sleep(10 / 1000.0)

    def set_humidity_oversample(self, value):
        self.tph_settings.os_hum = value
        self._set_bits(0x72, 0X07, 0, value)

    def get_humidity_oversample(self):
        return (self._get_regs(0x72, 1) & 0X07) >> 0

    def set_pressure_oversample(self, value):
        self.tph_settings.os_pres = value
        self._set_bits(0x74, 0X1C, 2, value)

    def get_pressure_oversample(self):
        return (self._get_regs(0x74, 1) & 0X1C) >> 2

    def set_temperature_oversample(self, value):
        self.tph_settings.os_temp = value
        self._set_bits(0x74, 0XE0, 5, value)

    def get_temperature_oversample(self):
        return (self._get_regs(0x74, 1) & 0XE0) >> 5

    def set_filter(self, value):
        self.tph_settings.filter = value
        self._set_bits(0x75, 0X1C, 2, value)

    def get_filter(self):
        return (self._get_regs(0x75, 1) & 0X1C) >> 2

    def select_gas_heater_profile(self, value):
        if value > 9 or value < 0:
            raise ValueError("Profile '{}' should be between {} and {}".format(value, NBCONV_MIN, NBCONV_MAX))

        self.gas_settings.nb_conv = value
        self._set_bits(0x71, 0X0F, 0, value)

    def get_gas_heater_profile(self):
        return self._get_regs(0x71, 1) & 0X0F

    def set_gas_status(self, value):
        self.gas_settings.run_gas = value
        self._set_bits(0x71, 0x10, 4, value)

    def get_gas_status(self):
        return (self._get_regs(0x71, 1) & 0x10) >> 4

    def set_gas_heater_profile(self, temperature, duration, nb_profile=0):
        self.set_gas_heater_temperature(temperature, nb_profile=nb_profile)
        self.set_gas_heater_duration(duration, nb_profile=nb_profile)

    def set_gas_heater_temperature(self, value, nb_profile=0):
        if nb_profile > 9 or value < 0:
            raise ValueError("Profile '{}' should be between {} and {}".format(nb_profile, NBCONV_MIN, NBCONV_MAX))

        self.gas_settings.heatr_temp = value
        temp = int(self._calc_heater_resistance(self.gas_settings.heatr_temp))
        self._set_regs(0x5a + nb_profile, temp)

    def set_gas_heater_duration(self, value, nb_profile=0):
        if nb_profile > 9 or value < 0:
            raise ValueError("Profile '{}' should be between {} and {}".format(nb_profile, NBCONV_MIN, NBCONV_MAX))

        self.gas_settings.heatr_dur = value
        temp = self._calc_heater_duration(self.gas_settings.heatr_dur)
        self._set_regs(0x64 + nb_profile, temp)

    def set_power_mode(self, value, blocking=True):
        """Set power mode"""
        if value not in (0, 1):
            print("Power mode should be one of SLEEP_MODE or FORCED_MODE")

        self.power_mode = value

        self._set_bits(0x74, 0x03, 0, value)

        while blocking and self.get_power_mode() != self.power_mode:
            time.sleep(10 / 1000.0)

    def get_power_mode(self):
        self.power_mode = self._get_regs(0x74, 1)
        return self.power_mode

    def get_sensor_data(self):
        self.set_power_mode(1)

        for attempt in range(10):
            status = self._get_regs(0x1d, 1)

            if (status & 0x80) == 0:
                time.sleep(10 / 1000.0)
                continue

            regs = self._get_regs(0x1d, 15)

            self.data.status = regs[0] & 0x80
            # Contains the nb_profile used to obtain the current measurement
            self.data.gas_index = regs[0] & 0x0f
            self.data.meas_index = regs[1]

            adc_pres = (regs[2] << 12) | (regs[3] << 4) | (regs[4] >> 4)
            adc_temp = (regs[5] << 12) | (regs[6] << 4) | (regs[7] >> 4)
            adc_hum = (regs[8] << 8) | regs[9]
            adc_gas_res = (regs[13] << 2) | (regs[14] >> 6)
            gas_range = regs[14] & 0x0f

            self.data.status |= regs[14] & 0x20
            self.data.status |= regs[14] & 0x10

            self.data.heat_stable = (self.data.status & 0x10) > 0

            temperature = self._calc_temperature(adc_temp)
            self.data.temperature = temperature / 100.0
            self.ambient_temperature = temperature

            self.data.pressure = self._calc_pressure(adc_pres) / 100.0
            self.data.humidity = self._calc_humidity(adc_hum) / 1000.0
            self.data.gas_resistance = self._calc_gas_resistance(adc_gas_res, gas_range)
            return True

        return False

    def _set_bits(self, register, mask, position, value):
        temp = self._get_regs(register, 1)
        temp &= ~mask
        temp |= value << position
        self._set_regs(register, temp)

    def _set_regs(self, register, value):
        if isinstance(value, int):
            self._i2c.write_byte_data(self.i2c_addr, register, value)
        else:
            self._i2c.write_i2c_block_data(self.i2c_addr, register, value)

    def _get_regs(self, register, length):
        if length == 1:
            return self._i2c.read_byte_data(self.i2c_addr, register)
        else:
            return self._i2c.read_i2c_block_data(self.i2c_addr, register, length)

    def _calc_temperature(self, temperature_adc):
        var1 = (temperature_adc >> 3) - (self.calibration_data.par_t1 << 1)
        var2 = (var1 * self.calibration_data.par_t2) >> 11
        var3 = ((var1 >> 1) * (var1 >> 1)) >> 12
        var3 = ((var3) * (self.calibration_data.par_t3 << 4)) >> 14

        # Save teperature data for pressure calculations
        self.calibration_data.t_fine = (var2 + var3)
        calc_temp = (((self.calibration_data.t_fine * 5) + 128) >> 8)

        return calc_temp

    def _calc_pressure(self, pressure_adc):
        var1 = ((self.calibration_data.t_fine) >> 1) - 64000
        var2 = ((((var1 >> 2) * (var1 >> 2)) >> 11) *
            self.calibration_data.par_p6) >> 2
        var2 = var2 + ((var1 * self.calibration_data.par_p5) << 1)
        var2 = (var2 >> 2) + (self.calibration_data.par_p4 << 16)
        var1 = (((((var1 >> 2) * (var1 >> 2)) >> 13 ) *
                ((self.calibration_data.par_p3 << 5)) >> 3) +
                ((self.calibration_data.par_p2 * var1) >> 1))
        var1 = var1 >> 18

        var1 = ((32768 + var1) * self.calibration_data.par_p1) >> 15
        calc_pressure = 1048576 - pressure_adc
        calc_pressure = ((calc_pressure - (var2 >> 12)) * (3125))

        if calc_pressure >= (1 << 31):
            calc_pressure = ((calc_pressure // var1) << 1)
        else:
            calc_pressure = ((calc_pressure << 1) // var1)

        var1 = (self.calibration_data.par_p9 * (((calc_pressure >> 3) *
            (calc_pressure >> 3)) >> 13)) >> 12
        var2 = ((calc_pressure >> 2) *
            self.calibration_data.par_p8) >> 13
        var3 = ((calc_pressure >> 8) * (calc_pressure >> 8) *
            (calc_pressure >> 8) *
            self.calibration_data.par_p10) >> 17

        calc_pressure = (calc_pressure) + ((var1 + var2 + var3 +
            (self.calibration_data.par_p7 << 7)) >> 4)

        return calc_pressure

    def _calc_humidity(self, humidity_adc):
        temp_scaled = ((self.calibration_data.t_fine * 5) + 128) >> 8
        var1 = (humidity_adc - ((self.calibration_data.par_h1 * 16))) \
                - (((temp_scaled * self.calibration_data.par_h3) // (100)) >> 1)
        var2 = (self.calibration_data.par_h2
                * (((temp_scaled * self.calibration_data.par_h4) // (100))
                + (((temp_scaled * ((temp_scaled * self.calibration_data.par_h5) // (100))) >> 6)
                // (100)) + (1 * 16384))) >> 10
        var3 = var1 * var2
        var4 = self.calibration_data.par_h6 << 7
        var4 = ((var4) + ((temp_scaled * self.calibration_data.par_h7) // (100))) >> 4
        var5 = ((var3 >> 14) * (var3 >> 14)) >> 10
        var6 = (var4 * var5) >> 1
        calc_hum = (((var3 + var6) >> 10) * (1000)) >> 12

        return min(max(calc_hum,0),100000)

    def _calc_gas_resistance(self, gas_res_adc, gas_range):
        var1 = ((1340 + (5 * self.calibration_data.range_sw_err)) * (lookupTable1[gas_range])) >> 16
        var2 = (((gas_res_adc << 15) - (16777216)) + var1)
        var3 = ((lookupTable2[gas_range] * var1) >> 9)
        calc_gas_res = ((var3 + (var2 >> 1)) / var2)

        return calc_gas_res

    def _calc_heater_resistance(self, temperature):
        temperature = min(max(temperature,200),400)

        var1 = ((self.ambient_temperature * self.calibration_data.par_gh3) / 1000) * 256
        var2 = (self.calibration_data.par_gh1 + 784) * (((((self.calibration_data.par_gh2 + 154009) * temperature * 5) / 100) + 3276800) / 10)
        var3 = var1 + (var2 / 2)
        var4 = (var3 / (self.calibration_data.res_heat_range + 4))
        var5 = (131 * self.calibration_data.res_heat_val) + 65536
        heatr_res_x100 = (((var4 / var5) - 250) * 34)
        heatr_res = ((heatr_res_x100 + 50) / 100)

        return heatr_res

    def _calc_heater_duration(self, duration):
        if duration < 0xfc0:
            factor = 0

            while duration > 0x3f:
                duration /= 4
                factor += 1

            return int(duration + (factor * 64))

        return 0xff

class I2CAdapter(I2C):

    def read_byte_data(self, addr, register):
        return self.readfrom_mem(addr, register, 1)[0]

    def read_i2c_block_data(self, addr, register, length):
        return self.readfrom_mem(addr, register, length)

    def write_byte_data(self, addr, register, data):
        return self.writeto_mem(addr, register, data)

    def write_i2c_block_data(self, addr, register, data):
        return self.writeto_mem(addr, register, data)
