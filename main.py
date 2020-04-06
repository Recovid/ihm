# -*- coding: utf-8 -*-
from monitor.window import Window
import sys, getopt

def main(argv):
    fullscreen=False
    try:
        opts, args = getopt.getopt(argv,"fhm")
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
    w=Window(fullscreen, mock)
    w.run()

if __name__ == '__main__':
    main(sys.argv[1:])
