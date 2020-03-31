import math
import io
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from monitor.communication import *

def nominal_data(t_ms, fr_hz):
    assert isinstance(t_ms, int) and t_ms >= 0
    assert isinstance(fr_hz, float) and fr_hz >= 0
    t_rad           = t_ms/1000 * fr_hz * 2*math.pi
    cos             = math.cos(t_rad)
    sin             = math.sin(t_rad)
    volume_ml     = max(0, 500*sin)
    debit_lpm     = max(10,50*cos)
    paw_mbar      =        90*cos if cos>0 else 10*cos
    fio2_pct      = max(0, 50 + 2 * cos)
    vt_ml         = max(0, 1 + volume_ml)
    fr_pm         = max(0, fr_hz * 60 + 2 * cos) # sec
    pep_mbar      = max(0,  5 +  5 * cos)
    pip_mbar      = max(0, 50 + 50 * cos)
    pplat_mbar    = max(0, 40 + 40 * cos)
    time_data = TimeData(t_ms, volume_ml, debit_lpm, paw_mbar)
    input_data = InputData(fio2_pct, vt_ml, fr_pm, pep_mbar, pip_mbar, pplat_mbar)
    return DataMsg(time_data, input_data)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print ("Usage: main.py time(ms)")
        sys.exit(1)
    fr_pm = 25
    fr_hz = fr_pm / 60 # sec
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with io.open('nominal_cycle.txt','w') as nominal_cycle:
        for t_ms in range(0, int(sys.argv[1]), int(1000/fr_pm)):
            nominal_cycle.write(serialize_msg(nominal_data(t_ms, fr_hz)))
