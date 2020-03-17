# Main imports
from mqtt import MQTTClient
from network import WLAN
import machine, ujson, _thread
import time, sys
import gc

# Lib imports
from lib import mqtt

# Config dicts
detimotic_conf = None
conf = None

# Global vars
wlan = None
client = None
kill = False

def main():
    global kill

    setup_config()
    setup_connectivity()
    setup_sensors()

    try:
        while(1):
            pass
    except KeyboardInterrupt:
        print("KB INTERRUPT!")
        kill = True
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
    for sensor in conf['sensors']:
        _thread.start_new_thread(sensor_thread, (sensor,))

def sensor_thread(sensor):
    s = Sensor(sensor)
    s.sensor_logic()

def publish(id, message):
    client.publish(topic=detimotic_conf['gateway']['telemetry_topic'] + "/" + str(id), msg='{"value": ' + str(message) + '}')


def signal(id, event):
    client.publish(topic=detimotic_conf['gateway']['events_topic']+ "/" + str(id), msg='{"' + str(event) + '" : 1}')


class Sensor:
    sensor = None

    def __init__(self, s):
        self.sensor = s

    def sensor_logic(self):
        t = time.ticks_ms()
        s = __import__('sensors/' + str(self.sensor['name']))
        getattr(s, "setup")(self)
        while(1):
            while(time.ticks_ms() - t < self.sensor['wait_time']):
                if kill:
                    print(str(self.sensor['name']) + " thread exiting")
                    _thread.exit()
            getattr(s, "loop")(self)
            t = time.ticks_ms()

    def publish(self, id, message):
        try:
            uuid = self.sensor['metrics'][id]
        except:
            print("ERROR loading ID for metric: " + str(id) + " of sensor " + str(sensor['name']) + ". Cannot publish telemetry!")
            return
        publish(uuid, message)

    def signal(self, id, message):
        try:
            uuid = self.sensor['metrics'][id]
        except:
            print("ERROR loading ID for metric: " + str(id) + " of sensor " + str(sensor['name']) + ". Cannot signal event!")
            return
        signal(uuid, message)
