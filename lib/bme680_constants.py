POLL_PERIOD_MS = 10
I2C_ADDR_PRIMARY = 0x76
I2C_ADDR_SECONDARY = 0x77
CHIP_ID = 0x61
COEFF_SIZE = 41
COEFF_ADDR1_LEN = 25
COEFF_ADDR2_LEN = 16
FIELD_LENGTH = 15
FIELD_ADDR_OFFSET = 17
SOFT_RESET_CMD = 0xb6
OK = 0
E_NULL_PTR = -1
E_COM_FAIL = -2
E_DEV_NOT_FOUND = -3
E_INVALID_LENGTH = -4
W_DEFINE_PWR_MODE = 1
W_NO_NEW_DATA = 2
I_MIN_CORRECTION = 1
I_MAX_CORRECTION = 2
ADDR_RES_HEAT_VAL_ADDR = 0x00
ADDR_RES_HEAT_RANGE_ADDR = 0x02
ADDR_RANGE_SW_ERR_ADDR = 0x04
ADDR_SENS_CONF_START = 0x5A
ADDR_GAS_CONF_START = 0x64
FIELD0_ADDR = 0x1d
RES_HEAT0_ADDR = 0x5a
GAS_WAIT0_ADDR = 0x64
CONF_HEAT_CTRL_ADDR = 0x70
CONF_ODR_RUN_GAS_NBC_ADDR = 0x71
CONF_OS_H_ADDR = 0x72
MEM_PAGE_ADDR = 0xf3
CONF_T_P_MODE_ADDR = 0x74
CONF_ODR_FILT_ADDR = 0x75
COEFF_ADDR1 = 0x89
COEFF_ADDR2 = 0xe1
CHIP_ID_ADDR = 0xd0
SOFT_RESET_ADDR = 0xe0
ENABLE_HEATER = 0x00
DISABLE_HEATER = 0x08
DISABLE_GAS_MEAS = 0x00
ENABLE_GAS_MEAS = 0x01
OS_NONE = 0
OS_1X = 1
OS_2X = 2
OS_4X = 3
OS_8X = 4
OS_16X = 5
FILTER_SIZE_0 = 0
FILTER_SIZE_1 = 1
FILTER_SIZE_3 = 2
FILTER_SIZE_7 = 3
FILTER_SIZE_15 = 4
FILTER_SIZE_31 = 5
FILTER_SIZE_63 = 6
FILTER_SIZE_127 = 7
SLEEP_MODE = 0
FORCED_MODE = 1
RESET_PERIOD = 10
MEM_PAGE0 = 0x10
MEM_PAGE1 = 0x00
HUM_REG_SHIFT_VAL = 4
RUN_GAS_DISABLE = 0
RUN_GAS_ENABLE = 1
TMP_BUFFER_LENGTH = 40
REG_BUFFER_LENGTH = 6
FIELD_DATA_LENGTH = 3
GAS_REG_BUF_LENGTH = 20
GAS_HEATER_PROF_LEN_MAX  = 10
OST_SEL = 1
OSP_SEL = 2
OSH_SEL = 4
GAS_MEAS_SEL = 8
FILTER_SEL = 16
HCNTRL_SEL = 32
RUN_GAS_SEL = 64
NBCONV_SEL = 128
GAS_SENSOR_SEL = GAS_MEAS_SEL | RUN_GAS_SEL | NBCONV_SEL
NBCONV_MIN = 0
NBCONV_MAX = 9
GAS_MEAS_MSK = 0x30
NBCONV_MSK = 0X0F
FILTER_MSK = 0X1C
OST_MSK = 0XE0
OSP_MSK = 0X1C
OSH_MSK = 0X07
HCTRL_MSK = 0x08
RUN_GAS_MSK = 0x10
MODE_MSK = 0x03
RHRANGE_MSK = 0x30
RSERROR_MSK = 0xf0
NEW_DATA_MSK = 0x80
GAS_INDEX_MSK = 0x0f
GAS_RANGE_MSK = 0x0f
GASM_VALID_MSK = 0x20
HEAT_STAB_MSK = 0x10
MEM_PAGE_MSK = 0x10
SPI_RD_MSK = 0x80
SPI_WR_MSK = 0x7f
BIT_H1_DATA_MSK = 0x0F
GAS_MEAS_POS = 4
FILTER_POS = 2
OST_POS = 5
OSP_POS = 2
OSH_POS = 0
RUN_GAS_POS = 4
MODE_POS = 0
NBCONV_POS = 0
T2_LSB_REG = 1
T2_MSB_REG = 2
T3_REG = 3
P1_LSB_REG = 5
P1_MSB_REG = 6
P2_LSB_REG = 7
P2_MSB_REG = 8
P3_REG = 9
P4_LSB_REG = 11
P4_MSB_REG = 12
P5_LSB_REG = 13
P5_MSB_REG = 14
P7_REG = 15
P6_REG = 16
P8_LSB_REG = 19
P8_MSB_REG = 20
P9_LSB_REG = 21
P9_MSB_REG = 22
P10_REG = 23
H2_MSB_REG = 25
H2_LSB_REG = 26
H1_LSB_REG = 26
H1_MSB_REG = 27
H3_REG = 28
H4_REG = 29
H5_REG = 30
H6_REG = 31
H7_REG = 32
T1_LSB_REG = 33
T1_MSB_REG = 34
GH2_LSB_REG = 35
GH2_MSB_REG = 36
GH1_REG = 37
GH3_REG = 38
REG_FILTER_INDEX = 5
REG_TEMP_INDEX = 4
REG_PRES_INDEX = 4
REG_HUM_INDEX = 2
REG_NBCONV_INDEX = 1
REG_RUN_GAS_INDEX = 1
REG_HCTRL_INDEX = 0
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
        self.par_t1 = bytes_to_word(calibration[T1_MSB_REG], calibration[T1_LSB_REG])
        self.par_t2 = bytes_to_word(calibration[T2_MSB_REG], calibration[T2_LSB_REG], bits=16, signed=True)
        self.par_t3 = twos_comp(calibration[T3_REG], bits=8)
        self.par_p1 = bytes_to_word(calibration[P1_MSB_REG], calibration[P1_LSB_REG])
        self.par_p2 = bytes_to_word(calibration[P2_MSB_REG], calibration[P2_LSB_REG], bits=16, signed=True)
        self.par_p3 = twos_comp(calibration[P3_REG], bits=8)
        self.par_p4 = bytes_to_word(calibration[P4_MSB_REG], calibration[P4_LSB_REG], bits=16, signed=True)
        self.par_p5 = bytes_to_word(calibration[P5_MSB_REG], calibration[P5_LSB_REG], bits=16, signed=True)
        self.par_p6 = twos_comp(calibration[P6_REG], bits=8)
        self.par_p7 = twos_comp(calibration[P7_REG], bits=8)
        self.par_p8 = bytes_to_word(calibration[P8_MSB_REG], calibration[P8_LSB_REG], bits=16, signed=True)
        self.par_p9 = bytes_to_word(calibration[P9_MSB_REG], calibration[P9_LSB_REG], bits=16, signed=True)
        self.par_p10 = calibration[P10_REG]
        self.par_h1 = (calibration[H1_MSB_REG] << HUM_REG_SHIFT_VAL) | (calibration[H1_LSB_REG] & BIT_H1_DATA_MSK)
        self.par_h2 = (calibration[H2_MSB_REG] << HUM_REG_SHIFT_VAL) | (calibration[H2_LSB_REG] >> HUM_REG_SHIFT_VAL)
        self.par_h3 = twos_comp(calibration[H3_REG], bits=8)
        self.par_h4 = twos_comp(calibration[H4_REG], bits=8)
        self.par_h5 = twos_comp(calibration[H5_REG], bits=8)
        self.par_h6 = calibration[H6_REG]
        self.par_h7 = twos_comp(calibration[H7_REG], bits=8)
        self.par_gh1 = twos_comp(calibration[GH1_REG], bits=8)
        self.par_gh2 = bytes_to_word(calibration[GH2_MSB_REG], calibration[GH2_LSB_REG], bits=16, signed=True)
        self.par_gh3 = twos_comp(calibration[GH3_REG], bits=8)

    def set_other(self, heat_range, heat_value, sw_error):
        self.res_heat_range = (heat_range & RHRANGE_MSK) // 16
        self.res_heat_val = heat_value
        self.range_sw_err = (sw_error * RSERROR_MSK) // 16

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
