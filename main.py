# -*- coding: utf-8 -*-
from monitor.window import Window
import sys, getopt

def main(argv):
    fullscreen=False
    mock=False
    serial=None
    prefix=None
    try:
        opts, args = getopt.getopt(argv,"fhms:p:")
    except getopt.GetoptError:
        print('main.py [-f]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py [-f]')
            sys.exit()
        elif opt == '-f':
            fullscreen=True
        elif opt == '-m':
            mock=True
        elif opt == '-s':
            serial = arg
        elif opt == '-p':
            prefix = arg
    w=Window(fullscreen, mock, serial, prefix)
    w.run()

if __name__ == '__main__':
    main(sys.argv[1:])
