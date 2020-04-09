import unittest

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from monitor.communication import *

class TestCommonMsgStructure(unittest.TestCase):

    def test_missing_type(self):
        frame = "04400 Vol__:0000 Deb__:+025 Paw__:+020\tCS8:6F\n"
        self.assertEqual(parse_msg(frame), None)

    def test_missing_type_with_crc_collision(self):
        frame = "04400 Vol__:0000 Deb__:+025 Paw__:+020\tCS8:F4\n"
        self.assertEqual(parse_msg(frame), None)

    def test_missing_crc_value(self):
        frame = "DATA msec_:04280 Vol__:0000 Deb__:+010 Paw__:+008\tCS"
        self.assertEqual(parse_msg(frame), None)

    def test_wrong_crc(self):
        frame = "DATA msec_:04280 Vol__:0000 Deb__:+010 Paw__:+008\tCS8:73\n"
        self.assertEqual(parse_msg(frame), None)
