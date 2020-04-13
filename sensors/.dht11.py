from lib.dht11_driver import *

th= None

def setup(dm):
    global th

    th= DTH('P8',0)

def loop(dm):
    result= th.read()
    if result.is_valid():
        value= result.temperature
        print("Temperature: %d C" % value)
        dm.publish("temp",value)
