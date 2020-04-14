lookupTable1 = [2147483647, 2147483647, 2147483647, 2147483647,
        2147483647, 2126008810, 2147483647, 2130303777, 2147483647,
        2147483647, 2143188679, 2136746228, 2147483647, 2126008810,
        2147483647, 2147483647]

lookupTable2 = [4096000000, 2048000000, 1024000000, 512000000,
        255744255, 127110228, 64000000, 32258064,
        16016016, 8000000, 4000000, 2000000,
        1000000, 500000, 250000, 125000]

def bytes_to_word(msb, lsb, bits=16, signed=False):
    word = (msb << 8) | lsb
    if signed:
        word = twos_comp(word, bits)
    return word

def twos_comp(val, bits=16):
    if val & (1 << (bits - 1)) != 0:
        val = val - (1 << bits)
    return val

class FieldData:
    def __init__(self):
        self.status = None
        self.heat_stable = False
        self.gas_index = None
        self.meas_index = None
        self.temperature = None
        self.pressure = None
        self.humidity = None
        self.gas_resistance = None

class CalibrationData:
    def __init__(self):
        self.par_h1 = None
        self.par_h2 = None
        self.par_h3 = None
        self.par_h4 = None
        self.par_h5 = None
        self.par_h6 = None
        self.par_h7 = None
        self.par_gh1 = None
        self.par_gh2 = None
        self.par_gh3 = None
        self.par_t1 = None
        self.par_t2 = None
        self.par_t3 = None
        self.par_p1 = None
        self.par_p2 = None
        self.par_p3 = None
        self.par_p4 = None
        self.par_p5 = None
        self.par_p6 = None
        self.par_p7 = None
        self.par_p8 = None
        self.par_p9 = None
        self.par_p10 = None
        self.t_fine = None
        self.res_heat_range = None
        self.res_heat_val = None
        self.range_sw_err = None

    def set_from_array(self, calibration):
        self.par_t1 = bytes_to_word(calibration[34], calibration[33])
        self.par_t2 = bytes_to_word(calibration[2], calibration[1], bits=16, signed=True)
        self.par_t3 = twos_comp(calibration[3], bits=8)
        self.par_p1 = bytes_to_word(calibration[6], calibration[5])
        self.par_p2 = bytes_to_word(calibration[8], calibration[7], bits=16, signed=True)
        self.par_p3 = twos_comp(calibration[9], bits=8)
        self.par_p4 = bytes_to_word(calibration[12], calibration[11], bits=16, signed=True)
        self.par_p5 = bytes_to_word(calibration[14], calibration[13], bits=16, signed=True)
        self.par_p6 = twos_comp(calibration[16], bits=8)
        self.par_p7 = twos_comp(calibration[15], bits=8)
        self.par_p8 = bytes_to_word(calibration[20], calibration[19], bits=16, signed=True)
        self.par_p9 = bytes_to_word(calibration[22], calibration[21], bits=16, signed=True)
        self.par_p10 = calibration[23]
        self.par_h1 = (calibration[27] << 4) | (calibration[26] & 0x0F)
        self.par_h2 = (calibration[25] << 4) | (calibration[26] >> 4)
        self.par_h3 = twos_comp(calibration[28], bits=8)
        self.par_h4 = twos_comp(calibration[29], bits=8)
        self.par_h5 = twos_comp(calibration[30], bits=8)
        self.par_h6 = calibration[31]
        self.par_h7 = twos_comp(calibration[32], bits=8)
        self.par_gh1 = twos_comp(calibration[37], bits=8)
        self.par_gh2 = bytes_to_word(calibration[36], calibration[35], bits=16, signed=True)
        self.par_gh3 = twos_comp(calibration[38], bits=8)

    def set_other(self, heat_range, heat_value, sw_error):
        self.res_heat_range = (heat_range & 0x30) // 16
        self.res_heat_val = heat_value
        self.range_sw_err = (sw_error * 0xf0) // 16

class TPHSettings:
    def __init__(self):
        self.os_hum = None
        self.os_temp = None
        self.os_pres = None
        self.filter = None

class GasSettings:
    def __init__(self):
        self.nb_conv = None
        self.heatr_ctrl = None
        self.run_gas = None
        self.heatr_temp = None
        self.heatr_dur = None

class BME680Data:
    def __init__(self):
        self.chip_id = None
        self.dev_id = None
        self.intf = None
        self.mem_page = None
        self.ambient_temperature = None
        self.data = FieldData()
        self.calibration_data = CalibrationData()
        self.tph_settings = TPHSettings()
        self.gas_settings = GasSettings()
        self.power_mode = None
        self.new_fields = None
