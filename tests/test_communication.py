import unittest

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from monitor.communication import *
from monitor.data import SETTINGS
from monitor.alarms import AlarmType

class TestCommonMsgStructure(unittest.TestCase):

    def test_missing_type(self):
        frame = "04400 Vol__:0000 Deb__:+025 Paw__:+020\tCS8:6F\n"
        self.assertIsNone(parse_msg(frame))

    def test_missing_type_with_crc_collision(self):
        frame = "04400 Vol__:0000 Deb__:+025 Paw__:+020\tCS8:F4\n"
        self.assertIsNone(parse_msg(frame))

    def test_missing_crc_value(self):
        frame = "DATA msec_:04280 Vol__:0000 Deb__:+010 Paw__:+008\tCS"
        self.assertIsNone(parse_msg(frame))

    def test_wrong_crc(self):
        frame = "DATA msec_:04280 Vol__:0000 Deb__:+010 Paw__:+008\tCS8:73\n"
        self.assertIsNone(parse_msg(frame))

    def test_incomplete_msg(self):
        frame = "DAT\tCS8:6F\n"
        self.assertIsNone(parse_msg(frame))

class TestDataMsg(unittest.TestCase):

    def test_parse_serialize_identity(self):
        msg = DataMsg(timestamp_ms=123, volume_ml=1, debit_lpm=2, paw_mbar=3)
        self.assertEqual(msg, parse_msg(serialize_msg(msg)))

    def test_parse_missing_field(self):
        self.assertIsNone(DataMsg.with_args("Vol__:0100 Deb__:+010 Paw__:-008"))
        self.assertIsNone(DataMsg.with_args("msec_:004280 Deb__:+010 Paw__:-008"))
        self.assertIsNone(DataMsg.with_args("msec_:004280 Vol__:0100 Paw__:-008"))
        self.assertIsNone(DataMsg.with_args("msec_:004280 Vol__:0100 Deb__:-010"))

    def test_parse_unexpected_field(self):
        self.assertIsNone(DataMsg.with_args("msec_:004280 Vol__:0100 Deb__:+010 Paw__:-008 XxXxX:12"))

    def test_parse_missing_sign(self):
        self.assertIsNone(DataMsg.with_args("msec_:004280 Vol__:0100 Deb__:010 Paw__:-008"))
        self.assertIsNone(DataMsg.with_args("msec_:004280 Vol__:0100 Deb__:+010 Paw__:008"))

    def test_parse_wrong_digit_count(self):
        self.assertIsNone(DataMsg.with_args("msec_:00428 Vol__:0100 Deb__:+010 Paw__:-008"))
        self.assertIsNone(DataMsg.with_args("msec_:0042801 Vol__:0100 Deb__:+010 Paw__:-008"))
        self.assertIsNone(DataMsg.with_args("msec_:004280 Vol__:010 Deb__:+010 Paw__:-008"))
        self.assertIsNone(DataMsg.with_args("msec_:004280 Vol__:01001 Deb__:+010 Paw__:-008"))
        self.assertIsNone(DataMsg.with_args("msec_:004280 Vol__:0100 Deb__:+01 Paw__:-008"))
        self.assertIsNone(DataMsg.with_args("msec_:004280 Vol__:0100 Deb__:+0101 Paw__:-008"))
        self.assertIsNone(DataMsg.with_args("msec_:004280 Vol__:0100 Deb__:+010 Paw__:-00"))
        self.assertIsNone(DataMsg.with_args("msec_:004280 Vol__:0100 Deb__:+010 Paw__:-0081"))

class TestRespMsg(unittest.TestCase):

    def test_parse_serialize_identity(self):
        msg = RespMsg(ie_ratio=2.1, fr_pm=25, vte_ml=500, pcrete_cmH2O=10, vm_lpm=10, pplat_cmH2O=40, pep_cmH2O=5)
        self.assertEqual(msg, parse_msg(serialize_msg(msg)))

    def test_parse_missing_field(self):
        self.assertIsNone(RespMsg.with_args("FR___:25 VTe__:500 PCRET:50 VM___:+10 PPLAT:40 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:20 VTe__:500 PCRET:50 VM___:+10 PPLAT:40 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:25 PCRET:50 VM___:+10 PPLAT:40 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:25 VTe__:500 VM___:+10 PPLAT:40 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:25 VTe__:500 PCRET:50 PPLAT:40 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:25 VTe__:500 PCRET:50 VM___:+10 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:25 VTe__:500 PCRET:50 VM___:+10 PPLAT:40"))

    def test_parse_unexpected_field(self):
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:25 VTe__:500 PCRET:50 VM___:+10 PPLAT:40 PEP__:05 XxXxX:12"))

    def test_parse_missing_sign(self):
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:25 VTe__:500 PCRET:50 VM___:10 PPLAT:40 PEP__:05"))

    def test_parse_wrong_digit_count(self):
        self.assertIsNone(RespMsg.with_args("IE___:2 FR___:25 VTe__:500 PCRET:50 VM___:+10 PPLAT:40 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:201 FR___:25 VTe__:500 PCRET:50 VM___:+10 PPLAT:40 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:2 VTe__:500 PCRET:50 VM___:+10 PPLAT:40 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:251 VTe__:500 PCRET:50 VM___:+10 PPLAT:40 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:25 VTe__:50 PCRET:50 VM___:+10 PPLAT:40 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:25 VTe__:5001 PCRET:50 VM___:+10 PPLAT:40 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:25 VTe__:500 PCRET:5 VM___:+10 PPLAT:40 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:25 VTe__:500 PCRET:501 VM___:+10 PPLAT:40 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:25 VTe__:500 PCRET:50 VM___:+1 PPLAT:40 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:25 VTe__:500 PCRET:50 VM___:+101 PPLAT:40 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:25 VTe__:500 PCRET:50 VM___:+10 PPLAT:4 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:25 VTe__:500 PCRET:50 VM___:+10 PPLAT:401 PEP__:05"))
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:25 VTe__:500 PCRET:50 VM___:+10 PPLAT:40 PEP__:0"))
        self.assertIsNone(RespMsg.with_args("IE___:20 FR___:25 VTe__:500 PCRET:50 VM___:+10 PPLAT:40 PEP__:051"))

class TestSetMsg(unittest.TestCase):

    def test_parse_serialize_identity(self):
        for i, s in enumerate(SETTINGS):
            with self.subTest(setting=s):
                msg = SetMsg(s, i)
                self.assertEqual(msg, parse_msg(serialize_msg(msg)))

    def test_parse_unknown_setting(self):
        self.assertIsNone(SetMsg.with_args("XxXxX:12"))

    def test_serialize_unknown_setting(self):
        with self.assertRaises(AssertionError):
            serialize_msg(SetMsg("XxXxX", 12))

    def test_parse_missing_value(self):
        self.assertIsNone(SetMsg.with_args("VT___:"))

    def test_parse_wrong_digit_count(self):
        for k, s, n in SetMsg.SETTINGS:
            with self.subTest(setting=k):
                self.assertIsNone(SetMsg.with_args(f"{s}:{'0' * (n - 1)}"))
                self.assertIsNone(SetMsg.with_args(f"{s}:{'0' * (n + 1)}"))

    def test_serialize_value_too_large(self):
        for k, _, n in SetMsg.SETTINGS:
            with self.subTest(setting=k):
                with self.assertRaises(AssertionError):
                    serialize_msg(SetMsg(k, 10**n))

class TestAlarmMsg(unittest.TestCase):

    def test_parse_serialize_identity(self):
		exemplemessage = "PMAX PMIN BATT_C CPU_LOST IO_MUTE"
        msg = AlarmMsg(exemplemessage)
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

class TestSoftResetMsg(unittest.TestCase):

    def test_parse_serialize_identity(self):
        msg = SoftResetMsg()
        self.assertEqual(msg, parse_msg(serialize_msg(msg)))

    def test_parse_unexpected_args(self):
        self.assertIsNone(SoftResetMsg.with_args('a'))
        self.assertIsInstance(SoftResetMsg.with_args(' '), SoftResetMsg)
