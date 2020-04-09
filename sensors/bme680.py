import lib.bme680_driver as bme680
from lib.bme680_iaq import get_iaq
import time

sensor = None

def setup(dm):
    global sensor

    i2c_dev = bme680.I2CAdapter()
    sensor = bme680.BME680(i2c_device=i2c_dev)
    sensor.set_humidity_oversample(bme680.OS_2X)
    sensor.set_pressure_oversample(bme680.OS_4X)
    sensor.set_temperature_oversample(bme680.OS_8X)
    sensor.set_filter(bme680.FILTER_SIZE_3)


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
