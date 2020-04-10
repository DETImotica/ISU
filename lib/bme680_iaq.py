import time

burn_in_time = 900000
burn_in_data = []
start_time = None
gas_baseline = None
hum_baseline = 40.0
hum_weighting = 0.25

def get_iaq(hum, hres):
    global start_time, gas_baseline

    if start_time is None:
        start_time = time.ticks_ms()
    if time.ticks_ms() - start_time < burn_in_time:
        burn_in_data.append(hres)
        return None
    if gas_baseline is None:
        gas_baseline = sum(burn_in_data[-len(burn_in_data):]) / float(len(burn_in_data))


    hum_offset = hum - hum_baseline
    if hum_offset > 0:
        hum_score = (100 - hum_baseline - hum_offset)
        hum_score /= (100 - hum_baseline)
        hum_score *= (hum_weighting * 100)
    else:
        hum_score = (hum_baseline + hum_offset)
        hum_score /= hum_baseline
        hum_score *= (hum_weighting * 100)

    gas_offset = gas_baseline - hres
    if gas_offset > 0:
        gas_score = (hres / gas_baseline)
        gas_score *= (100 - (hum_weighting * 100))

    else:
        gas_score = 100 - (hum_weighting * 100)

    return hum_score + gas_score
