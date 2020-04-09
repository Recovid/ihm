import unittest

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from monitor.communication import *
from monitor.data import SETTINGS

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

    def test_incomplete_msg(self):
        frame = "DAT\tCS8:6F\n"
        self.assertEqual(parse_msg(frame), None)

class TestDataMsg(unittest.TestCase):

    def test_parse_serialize_identity(self):
        msg = DataMsg(timestamp_ms=123, volume_ml=1, debit_lpm=2, paw_mbar=3)
        self.assertEqual(msg, parse_msg(serialize_msg(msg)))

class TestRespMsg(unittest.TestCase):

    def test_parse_serialize_identity(self):
        msg = RespMsg(ie_ratio=2.1, fr_pm=25, vte_ml=500, pcrete_cmH2O=10, vm_lpm=10, pplat_cmH2O=40, pep_cmH2O=5)
        self.assertEqual(msg, parse_msg(serialize_msg(msg)))

class TestSetMsg(unittest.TestCase):

    def test_parse_serialize_identity(self):
        for i, s in enumerate(SETTINGS):
            with self.subTest(setting=s):
                msg = SetMsg(s, i)
                self.assertEqual(msg, parse_msg(serialize_msg(msg)))

class TestAlarmMsg(unittest.TestCase):

    def test_parse_serialize_identity(self):
        msg = AlarmMsg("msg")
        self.assertEqual(msg, parse_msg(serialize_msg(msg)))

class TestInitMsg(unittest.TestCase):

    def test_parse_serialize_identity(self):
        msg = InitMsg("msg")
        self.assertEqual(msg, parse_msg(serialize_msg(msg)))

class TestPauseBipMsg(unittest.TestCase):

    def test_parse_serialize_identity(self):
        msg = PauseBipMsg(123)
        self.assertEqual(msg, parse_msg(serialize_msg(msg)))

class TestPauseInsMsg(unittest.TestCase):

    def test_parse_serialize_identity(self):
        msg = PauseInsMsg(123)
        self.assertEqual(msg, parse_msg(serialize_msg(msg)))

class TestPauseExpMsg(unittest.TestCase):

    def test_parse_serialize_identity(self):
        msg = PauseExpMsg(123)
        self.assertEqual(msg, parse_msg(serialize_msg(msg)))
