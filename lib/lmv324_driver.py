import pycom
import time
import machine
import math
from machine import Pin, ADC

class LMV324:

    NUM_SOUND_MEAN= 50
    NUM_SOUND_LOOPS= 4
    
    def __init__ (self, pin):
        adc= ADC (bits= 12)
        self.apin= adc.channel (pin= pin, attn= ADC.ATTN_11DB)

    def dbRead (self):
        
        decibel_value= [0] * (LMV34.NUM_SOUND_LOOPS * LMV34.NUM_SOUND_MEAN + 1)
        decibel_mean= [0] * (LMV34.NUM_SOUND_LOOPS + 1) 
        decibel_mean[1]= 0
        decibel_mean[2]= 0
        decibel_mean[3]= 0
        decibel_mean[4]= 0
        channel_0= -1
        value_1 = 0.0

        for i in range (0,LMV34.NUM_SOUND_LOOPS):
            for j in range (0,LMV34.NUM_SOUND_MEAN):
                while (channel_0 < 0) or (channel_0 > 4000):
                    channel_0= self.apin()      
                analog_0 = (float) (channel_0 * 5.0 / 4095.0)
                if channel_0 <= 180:
                    decibel_value[(i-1)*50+j] = 36 + 20*math.log(analog_0+0.316,10)
                elif ((channel_0 > 180) and (channel_0 <= 500)):
                    decibel_value[(i-1)*50+j] = 30 + 20*math.log(5*(analog_0+0.39),10)
                elif ((channel_0 > 500) and (channel_0 <= 800)):
                    decibel_value[(i-1)*50+j] = 40 + 20*math.log(5*(analog_0+0.03),10)
                elif ((channel_0 > 800) and (channel_0 <= 1200)):
                    decibel_value[(i-1)*50+j] = 40 + 20*math.log(5*analog_0, 10);
                elif ((channel_0 > 1200) and (channel_0 <= 2500)):
                    decibel_value[(i-1)*50+j] = 64 + 20*math.log(10*(analog_0+0.316),10)
                elif ((channel_0 > 2500) and (channel_0 < 4000)):
                    decibel_value[(i-1)*50+j] = 80 + 20*math.log(20*analog_0, 10)
                decibel_mean[i] = decibel_mean[i] + decibel_value[(i-1)*50+j]
                channel_0 = -1  
                time.sleep(0.05)
            decibel_mean[i] = decibel_mean[i]/LMV34.NUM_SOUND_MEAN        
        for i in range (0,LMV34.NUM_SOUND_LOOPS):
            value_1 = value_1 + decibel_mean[i]
        value_1 = value_1/LMV34.NUM_SOUND_LOOPS
        return (int) (value_1)           