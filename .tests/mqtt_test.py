from mqtt import MQTTClient
from network import WLAN
import machine
import time

def sub_cb(topic, msg):
   print(msg)

wlan = WLAN(mode=WLAN.STA)
wlan.connect("PEI_TestNet", auth=(WLAN.WPA2, "DETImotic"), timeout=5000)

while not wlan.isconnected():
    machine.idle()
print("Connected to WiFi\n")

client = MQTTClient("device_id", "192.168.0.2",user="detimotic", password="testpw", port=1883)

client.set_callback(sub_cb)
client.connect()
client.subscribe(topic="t")

while True:
    print("Sending ON")
    client.publish(topic="t", msg="ON")
    time.sleep(1)
    print("Sending OFF")
    client.publish(topic="t", msg="OFF")
    client.check_msg()

    time.sleep(1)
