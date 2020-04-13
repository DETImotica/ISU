import lib.bme680_driver as bme680
import time

sensor = None

burn_in_time = 900000
burn_in_data = 0
burn_in_len = 0
start_time = None
gas_baseline = None
hum_baseline = 40.0
hum_weighting = 0.25

def setup(dm):
    global sensor

    i2c_dev = bme680.I2CAdapter()
    sensor = bme680.BME680(i2c_device=i2c_dev)
    sensor.set_humidity_oversample(2)
    sensor.set_pressure_oversample(3)
    sensor.set_temperature_oversample(4)
    sensor.set_filter(2)


def loop(dm):
    if sensor.get_sensor_data():
        iaq = get_iaq(sensor.data.humidity, sensor.data.gas_resistance)

        print("{} C, {} hPa, {} RH, {} RES,".format(
                sensor.data.temperature,
                sensor.data.pressure,
                sensor.data.humidity,
                sensor.data.gas_resistance))

        dm.publish("temp", sensor.data.temperature)
        dm.publish("hum", sensor.data.humidity)
        dm.publish("pres", sensor.data.pressure)

        if iaq is not None:
            print("{} IAQ".format(iaq))
            dm.publish("iaq", iaq)

def get_iaq(hum, hres):
    global start_time, gas_baseline, burn_in_data, burn_in_len

    if start_time is None:
        start_time = time.ticks_ms()
    if time.ticks_ms() - start_time < burn_in_time:
        burn_in_data += hres
        burn_in_len += 1.0
        return None
    if gas_baseline is None:
        gas_baseline = burn_in_data / burn_in_len


    hum_offset = hum - hum_baseline
    if hum_offset > 0:
        hum_score = (100 - hum_baseline - hum_offset)
        hum_score /= (100 - hum_baseline)
        hum_score *= (hum_weighting * 100)
    else:
        hum_score = (hum_baseline + hum_offset)
        hum_score /= hum_baseline
        hum_score *= (hum_weighting * 100)

    gas_offset = gas_baseline - hres
    if gas_offset > 0:
        gas_score = (hres / gas_baseline)
        gas_score *= (100 - (hum_weighting * 100))

    else:
        gas_score = 100 - (hum_weighting * 100)

    return hum_score + gas_score
