from lib.lmv324_driver import *

lmv= None

def setup (dm):
    global lmv
    
    lmv= LMV324 ('P13')

def loop (dm):
    value= lmv.dbRead()
    print("Audio Value: "+ str(value))
    dm.publish("db", value)
    