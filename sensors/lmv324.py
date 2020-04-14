from lib.lmv324_driver import *
import _thread, gc

lmv= None
#lock = None

def setup(dm):
    global lmv
#    global lock

    lmv= LMV324 ('P13')
#    lock = _thread.allocate_lock()

def loop(dm):
    value= lmv.dbRead()
    print("Audio Value: "+ str(value))
    dm.publish("db", value)
#    global lock
#    _thread.stack_size(4096)
#    if not lock.locked():
#        with lock:
#            gc.collect()
#            print('mem: ' + str(gc.mem_free()))
#            try:
#                _thread.start_new_thread(loop_th, (dm,))
#            except:
#                print("Error creating lmv324 thread")


#def loop_th(dm):
#    global lock
#    with lock:
#        value= lmv.dbRead()
#        print("Audio Value: "+ str(value))
#        dm.publish("db", value)
#        _thread.exit()
