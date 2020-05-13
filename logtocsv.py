
# -*- coding: utf-8 -*-
from monitor.window import Window
from monitor.communication import *
import sys, getopt

def main(argv):
    #Each parameter is a filename
    #It will only process filename ending with .log but not containing tsi
    for name in argv:
        if "tsi" in name or not name.endswith(".log"):
            continue
        print(name)
        csvfile = open(name+".csv", "w")
        start_cycle=False
        with open(name, "rb") as logfile:
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
                        print(timestamp, msg.timestamp_ms, msg.paw_mbar, msg.debit_lpm, msg.volume_ml, start_cycle_bit, file=csvfile, sep="\t")
                    elif isinstance(msg, RespMsg):
                        start_cycle=True
            csvfile.close()


if __name__ == '__main__':
    main(sys.argv[1:])
