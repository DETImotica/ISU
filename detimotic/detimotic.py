# Main imports
from network import WLAN
import machine, ujson, _thread
import time, sys, gc

# Lib imports
from lib.mqtt import MQTTClient

# Config dicts
detimotic_conf = None
conf = None

# Global vars
wlan = None
client = None
modules = []

def main():
    setup_config()
    setup_connectivity()
    gc.collect()
    setup_sensors()

    try:
        while True:
            #try:
            for i in range(len(modules)):
                module, last = modules[i]
                if time.ticks_ms() - last >= module.time():
                    gc.collect()
                    module.loop()
                    modules[i] = (module, time.ticks_ms())
            #except MemoryError:
            #    print('Memory Error!')
    except KeyboardInterrupt:
        print("KB INTERRUPT!")
        wlan.disconnect()
        gc.collect()
        sys.exit(2)


def setup_config():
    global detimotic_conf
    global conf

    # TODO: Parse config to verify data integrity

    try:
        with open('detimotic/detimotic_conf.json') as json_file:
            detimotic_conf = ujson.load(json_file)
    except:
        print("ERROR loading detimotic configuration file!")
        sys.exit(1)

    try:
        with open('conf.json') as json_file:
            conf = ujson.load(json_file)
    except:
        print("ERROR loading ISU configuration file!")
        sys.exit(2)

def setup_connectivity():
    global wlan
    global client

    wlan = WLAN(mode=WLAN.STA)
    wlan.connect(detimotic_conf['wifi']['ssid'], auth=(WLAN.WPA2, detimotic_conf['wifi']['passw']), timeout=5000)

    while not wlan.isconnected():
        machine.idle()
    print("Connected to WiFi")

    client = MQTTClient("device_id", detimotic_conf['gateway']['addr'],user=detimotic_conf['gateway']['uname'], password=detimotic_conf['gateway']['passw'], port=detimotic_conf['gateway']['port'])
    client.connect()

    print("Connected to MQTT gateway\n")


def setup_sensors():
    for module in conf['modules']:
        if module['active']:
            s = Module(module)
            s.setup()
            modules.append((s, 0))

def publish(id, message):
    try:
        client.publish(topic=detimotic_conf['gateway']['telemetry_topic'] + "/" + str(id), msg='{"value": ' + str(message) + '}')
    except:
        print("Error publishing: {}".format(message))

def signal(id, event):
    try:
        client.publish(topic=detimotic_conf['gateway']['events_topic']+ "/" + str(id), msg='{"' + str(event) + '" : 1}')
    except:
        print("Error signaling: {}".format(event))

class Module:
    _module = None
    _instance = None

    def __init__(self, s):
        self._module = s

    def setup(self):
        self._instance = __import__('sensors/' + str(self._module['name']))
        print('Starting module ' + str(self._module['name']))
        getattr(self._instance, "setup")(self)

    def loop(self):
        getattr(self._instance, "loop")(self)

    def time(self):
        return self._module['wait_time']

    def publish(self, id, message):
        try:
            uuid = self._module['metrics'][id]
        except:
            print("ERROR loading ID for metric: " + str(id) + " of sensor " + str(_module['name']) + ". Cannot publish telemetry!")
            return
        publish(uuid, message)

    def signal(self, id, message):
        try:
            uuid = self._module['events'][id]
        except:
            print("ERROR loading ID for metric: " + str(id) + " of sensor " + str(_module['name']) + ". Cannot signal event!")
            return
        signal(uuid, message)
