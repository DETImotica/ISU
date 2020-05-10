# Main imports
from network import WLAN
from crypto import AES
from ubinascii import b2a_base64
import machine, ujson, _thread, crypto
import time, sys, gc
from machine import WDT

# Lib imports
from lib.mqtt import MQTTClient

# Config dicts
detimotic_conf = None
conf = None

# Global vars
wlan = None
client = None
modules = []
watchdog = None

def main():
    global watchdog

    setup_config()
    setup_connectivity()
    gc.collect()
    setup_sensors()

    watchdog = WDT(timeout=detimotic_conf['watchdog'])

    try:
        while True:
            try:
                for i in range(len(modules)):
                    watchdog.feed()
                    module, last = modules[i]
                    if time.ticks_ms() - last >= module.time():
                        gc.collect()
                        module.loop()
                        modules[i] = (module, time.ticks_ms())
                if time.ticks_ms() - client.last_pingreq >= detimotic_conf['gateway']['ping_freq']:
                    client.ping()
                elif time.ticks_ms() - client.last_pingresp >= 3*detimotic_conf['gateway']['ping_freq']:
                    print('Forcibly reconnecting!')
                    client.disconnect()
                    wlan.disconnect()
                    watchdog.feed()
                    setup_connectivity()
                client.check_msg()
            except MemoryError:
                print('Memory Error!')
    except KeyboardInterrupt:
        print("KB INTERRUPT!")
        client.disconnect()
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

    client = MQTTClient(conf['isu_id'], detimotic_conf['gateway']['addr'],user=detimotic_conf['gateway']['uname'], password=detimotic_conf['gateway']['passw'], port=detimotic_conf['gateway']['port'])
    client.connect()

    print("Connected to MQTT gateway\n")


def setup_sensors():
    for module in conf['modules']:
        if module['active']:
            s = Module(module)
            s.setup()
            modules.append((s, 0))

def publish(id, message):
    if message is None:
        return
    try:
        client.publish(topic=detimotic_conf['gateway']['telemetry_topic'] + "/" + str(id), msg=message)
    except:
        print("Error publishing for metric: {}".format(id))

def signal(id, event):
    if event is None:
        return
    try:
        client.publish(topic=detimotic_conf['gateway']['events_topic']+ "/" + str(id), msg=event)
    except:
        print("Error signaling event: {}".format(event))

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
            uuid = self._module['metrics'][id]['id']
        except:
            print("ERROR loading ID for metric: " + str(id) + " of sensor " + str(self._module['name']) + ". Cannot publish telemetry!")
            return
        publish(uuid, self._encrypt(id, '{"value": ' + str(message) + '}'))

    def signal(self, id, message):
        try:
            uuid = self._module['events'][id]['id']
        except:
            print("ERROR loading ID for metric: " + str(id) + " of sensor " + str(self._module['name']) + ". Cannot signal event!")
            return
        signal(uuid, self._encrypt(id, '{"' + str(message) + '" : 1}'))

    def _encrypt(self, id, message):
        gc.collect()
        try:
            iv = crypto.getrandbits(128)
            cipher = AES(self._module['metrics'][id]['key'].encode('utf-8'), AES.MODE_CFB, iv)
            return b2a_base64(iv + cipher.encrypt(message.encode('utf-8'))).decode('utf-8')
        except:
            print("ERROR encrypting message for metric: " + str(id) + " of sensor " + str(self._module['name']) + ". Cannot proceed!")
            return None
