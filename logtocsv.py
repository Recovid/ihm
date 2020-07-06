
# -*- coding: utf-8 -*-
from monitor.communication import *
import sys, getopt

def main(argv):
    #Each parameter is a filename
    #It will only process filename ending with .log but not containing tsi
    for name in argv:
        if not name.endswith(".log"):
            continue
        if "tsi" in name :
            print(name)
            csvfile = open(name+".csv", "w")
            last_time_rpi=0
            with open(name, "r") as logfile:
                print('time', 'val', file=csvfile, sep="\t")
                for line in logfile:
                    sline = line.split("\t")
                    if(len(sline)!=3):
                        print(line)
                        print(sline)
                        continue
                    time = int(sline[0])
                    val = float(sline[1])
                    start = int(sline[2])
                    if start:
                        last_time_rpi=time
                    else:
                        time=last_time_rpi+10
                        last_time_rpi=time
                    print(time, val, file=csvfile, sep="\t")
        else:
            print(name)
            csvfile = open(name+".csv", "w")
            start_cycle=False
            Patmo = 0
            TempC = 0
            last_time_reco=0
            last_time_rpi=0
            with open(name, "rb") as logfile:
                print('timestamp', 'paw_mbar', 'debit_lpm', 'volume_ml', 'state', 'slm', 'Patmo', 'TempC', 'start_cycle_bit', file=csvfile, sep="\t")
                for line in logfile:
                    try:
                        line = line.decode("ascii")
                    except:
                        print("Exception when decoding the line in the serial port")
                    else :
                        sline = line.split("\t")
                        if(len(sline)!=3):
                            print(line)
                            print(sline)
                            continue
                        timestamp = int(sline[0])
                        line = sline[1]+"\t"+sline[2]
                        msg = parse_msg(line)
                        if isinstance(msg, DataMsg):
                            start_cycle_bit = 0
                            if start_cycle:
                                start_cycle_bit = 1
                                start_cycle=False
                                last_time_reco=msg.timestamp_ms
                                last_time_rpi=timestamp
                            else:
                                dt = (msg.timestamp_ms-last_time_reco + (1 << 19)) % (1 << 19) # handle overflow
                                last_time_reco=msg.timestamp_ms
                                timestamp = last_time_rpi+dt
                                last_time_rpi = timestamp
                            print(timestamp, msg.paw_mbar, msg.debit_lpm, msg.volume_ml, msg.state, msg.slm, Patmo, TempC / 10., start_cycle_bit, file=csvfile, sep="\t")
                        elif isinstance(msg, RespMsg):
                            Patmo = msg.Patmo
                            TempC = msg.Temp
                            start_cycle=True
                csvfile.close()


if __name__ == '__main__':
    main(sys.argv[1:])
