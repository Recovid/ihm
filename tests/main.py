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
    return DataMsg(t_ms, volume_ml, debit_lpm, paw_mbar)

def resp_msg(fr_hz):
    return RespMsg(fio2_pct=50, vt_ml=500, fr_pm=fr_hz * 60, pep_mbar=5, pip_mbar=50, pplat_mbar=40)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print ("Usage: main.py time(ms)")
        sys.exit(1)
    fr_pm = 25
    fr_hz = fr_pm / 60 # sec
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with io.open('nominal_cycle.txt','w') as nominal_cycle:
        nominal_cycle.write(serialize_msg(SetMsg(Data.VT, 350)))
        nominal_cycle.write(serialize_msg(SetMsg(Data.FR, 19)))
        nominal_cycle.write(serialize_msg(SetMsg(Data.PEP, 6)))
        nominal_cycle.write(serialize_msg(SetMsg(Data.FLOW,58)))
        nominal_cycle.write(serialize_msg(SetMsg(Data.TPLAT,200)))
        nominal_cycle.write(serialize_msg(resp_msg(fr_hz)))
        for t_ms in range(0, int(sys.argv[1]), int(1000/fr_pm)):
            nominal_cycle.write(serialize_msg(nominal_data(t_ms, fr_hz)))
        nominal_cycle.write(serialize_msg(SetMsg(Data.VT, 350)))
        nominal_cycle.write(serialize_msg(SetMsg(Data.FR, 19)))
        nominal_cycle.write(serialize_msg(SetMsg(Data.PEP, 6)))
        nominal_cycle.write(serialize_msg(SetMsg(Data.FLOW,58)))
        nominal_cycle.write(serialize_msg(resp_msg(fr_hz)))
