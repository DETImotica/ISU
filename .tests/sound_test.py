import math
import time
import pycom
import machine
from machine import Pin, ADC

#def pin_handler(arg):
    #print("got an interrupt in pin %s" % (arg.id()))

adc= ADC(bits=12)
#Initialize sensor pins

#gate= Pin('P21', mode=Pin.IN, pull=None)
#gate.callback(Pin.IRQ_FALLING | Pin.IRQ_RISING, pin_handler)
apin= adc.channel(pin='P13', attn= ADC.ATTN_11DB)
while True:
    time.sleep(0.1)
    value= apin()
    #if value > 0:
    print("Envelope: "+ str(value))
