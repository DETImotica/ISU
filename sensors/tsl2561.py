from lib.tsl2561_driver import *

lux_sensor = None

def setup(dm):
    global lux_sensor

    lux_sensor = device()
    lux_sensor.init()

def loop(dm):
    value = lux_sensor.getLux()
    print("Lux value: " + str(value))
    dm.publish("lux", value)
