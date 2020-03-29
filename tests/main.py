import math
import io
import os

class Data: # TODO move to communication.py
    number = -1 # invalid
    volume_ml = -1
    debit_lpm =  -100
    paw_mbar = -1
    fio2_pct = -1
    vt_ml = -1
    fr_pm = -1
    pep_mbar = -1
    debit_max_lpm = -1

def nominal_data(t_ms, fr_hz):
    assert isinstance(t_ms, int) and t_ms >= 0
    assert isinstance(fr_hz, float) and fr_hz >= 0
    d = Data()
    d.number        = t_ms
    t_rad           = t_ms/1000 * fr_hz * 2*math.pi
    cos             = math.cos(t_rad)
    sin             = math.sin(t_rad)
    d.volume_ml     = max(0, 500*sin)
    d.debit_lpm     = max(10,50*cos)
    d.paw_mbar      =        90*cos if cos>0 else 10*cos
    d.fio2_pct      = max(0, 50 + 2 * cos)
    d.vt_ml         = max(0, 1 + d.volume_ml)
    d.fr_pm         = max(0, fr_hz * 60 + 2 * cos) # sec
    d.pep_mbar      = max(0,  5 +  5 * cos)
    d.debit_max_lpm = max(0, 40 + 40 * cos)
    return d

def checksum8(frame):
    assert isinstance(frame, str)
    return sum(ord(c) for c in frame) % 256

def checked_frame(frame):
    assert isinstance(frame, str)
    frame += " CS8_:"
    return frame + "%02X\n" % checksum8(frame)

def data_frame(d):
    assert isinstance(d, Data)
    return checked_frame( \
        "DATA msec:%05d Vol_:%03d Deb_:%s%03d Paw_:%s%03d Fi02:%03d Vt__:%04d FR__:%02d PEP_:%02d DebM:%02d" \
        % (d.number, d.volume_ml, '-' if d.debit_lpm<0 else '+', d.debit_lpm, '-' if d.paw_mbar<0 else '+', abs(d.paw_mbar), d.fio2_pct, d.vt_ml, d.fr_pm, d.pep_mbar, d.debit_max_lpm))

if __name__ == '__main__':
    fr_pm = 25
    fr_hz = fr_pm / 60 # sec
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with io.open('nominal_cycle.txt','w') as nominal_cycle:
        for t_ms in range(0, int(1000/fr_hz), int(1000/fr_pm)):
            nominal_cycle.write(data_frame(nominal_data(t_ms, fr_hz)))
