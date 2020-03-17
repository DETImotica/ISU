from network import Bluetooth

bt = None

def setup(dm):
    global bt

    bt = Bluetooth()
    bt.start_scan(-1)

def loop(dm):
    macs = []
    advs = bt.get_advertisements()
    for adv in advs:
        macs.append(adv.mac)
    value = len(set(macs))

    print("Number of BLE devices currently advertising: " + str(value))
    dm.publish("device_num", value)
