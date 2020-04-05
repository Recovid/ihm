import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from monitor.communication import *

## Incomplete frame
frame = "04400 Vol__:0000 Deb__:+025 Paw__:+020	CS8:6F\n"
assert(parse_msg(frame) == None)

## Incomplete frame
frame = "DATA msec_:04280 Vol__:0000 Deb__:+010 Paw__:+008	CS"
assert(parse_msg(frame) == None)

## Wrong CRC
frame = "DATA msec_:04280 Vol__:0000 Deb__:+010 Paw__:+008	CS8:73\n"
assert(parse_msg(frame) == None)

## Incomplete frame with CRC collision
frame = "04400 Vol__:0000 Deb__:+025 Paw__:+020	CS8:F4\n"
assert(parse_msg(frame) == None)
