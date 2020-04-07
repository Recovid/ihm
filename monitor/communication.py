#!/usr/bin/python

import re
import sys
from .data import Data

class DataMsg:
    args_pattern = re.compile('^msec_:(\d{6}) Vol__:(\d{4}) Deb__:([+-]\d{3}) Paw__:([+-]\d{3})$')

    def __init__(self, timestamp_ms, volume_ml, debit_lpm, paw_mbar):
        self.timestamp_ms = timestamp_ms
        self.volume_ml = volume_ml
        self.debit_lpm = debit_lpm
        self.paw_mbar = paw_mbar

    def with_args(args_str):
        match = re.match(DataMsg.args_pattern, args_str)
        if not match:
            print("failed to parse DATA message", file=sys.stderr)
            return None
        return DataMsg(*[int(g) for g in match.groups()[0:4]])

    def __str__(self):
        args = (self.timestamp_ms % 1000000, self.volume_ml, '-' if self.debit_lpm < 0 else '+', self.debit_lpm, '-' if self.paw_mbar < 0 else '+', abs(self.paw_mbar))
        return 'DATA msec_:%06d Vol__:%04d Deb__:%s%03d Paw__:%s%03d' % args

class RespMsg:
    args_pattern = re.compile('^IE___:(\d{2}) FR___:(\d{2}) VTe__:(\d{3}) PCRET:(\d{2}) VM___:([+-]\d{2}) PPLAT:(\d{2}) PEP__:(\d{2})$')

    def __init__(self, ie_ratio, fr_pm, vte_ml, pcrete_cmH2O, vm_lpm, pplat_cmH2O, pep_cmH2O):
        self.ie_ratio = ie_ratio
        self.fr_pm = fr_pm
        self.vte_ml = vte_ml
        self.pcrete_cmH2O = pcrete_cmH2O
        self.vm_lpm = vm_lpm
        self.pplat_cmH2O = pplat_cmH2O
        self.pep_cmH2O = pep_cmH2O

    def with_args(args_str):
        match = re.match(RespMsg.args_pattern, args_str)
        if not match:
            print("failed to parse RESP message", file=sys.stderr)
            return None
        return RespMsg(*[int(g) for g in match.groups()[0:7]])

    def __str__(self):
        args = (self.ie_ratio * 10, self.fr_pm, self.vte_ml, self.pcrete_cmH2O, '-' if self.vm_lpm < 0 else '+', self.vm_lpm, self.pplat_cmH2O, self.pep_cmH2O)
        return 'RESP IE___:%02d FR___:%02d VTe__:%03d PCRET:%02d VM___:%s%02d PPLAT:%02d PEP__:%02d' % args

class SetMsg:
    args_pattern = re.compile('^(\w{5}):(\d{2,5})$')
    SETTINGS = [ # (setting key, serial string, number of digits)
        # resp settings
        (Data.VT, "VT___", 3),
        (Data.FR, "FR___", 2),
        (Data.PEP, "PEP__", 2),
        (Data.FLOW, "FLOW_", 2),
        (Data.TPLAT, "Tplat", 4),
        (Data.IE, "IE", 2),
        # alarms
        (Data.VTMIN, "VTmin", 4),
        (Data.PMAX, "Pmax_", 3),
        (Data.PMIN, "Pmin_", 3),
        (Data.FRMIN, "FRmin", 2),
        (Data.VMMIN, "VMmin", 4)

    ]

    def __init__(self, setting, value):
        self.setting = setting
        self.value = value

    def with_args(args_str):
        match = re.match(SetMsg.args_pattern, args_str)
        if not match:
            print("failed to parse SET_ message:", args_str, file=sys.stderr)
            return None
        for k, s, n in SetMsg.SETTINGS:
            if s == match.group(1):
                # TODO: check number of digits (len(match.group(2)) == n)
                return SetMsg(k, int(match.group(2)))

        print("unknown setting:", match.group(1), file=sys.stderr)
        return None

    def __str__(self):
        for k, s, n in SetMsg.SETTINGS:
            if self.setting == k:
                # TODO: check self.value fits on n digits
                return ('SET_ %s:%0{}d'.format(n)) % (s, self.value)
        assert False, "unknown setting: " + self.setting

class AlarmMsg:
    def __init__(self, text):
        self.text = text

    def with_args(args_str):
        # TODO: check alarm text is valid
        return AlarmMsg(args_str)

    def __str__(self):
        return 'ALRM %s' % self.text

class InitMsg:
    def __init__(self, text):
        self.text = text

    def with_args(args_str):
        return InitMsg(args_str)

    def __str__(self):
        return 'INIT %s' % self.text

class AckAlarmMsg:
    def __init__(self, alarm_msg):
        self.alarm_msg = alarm_msg

    def with_args(args_str):
        alarm_msg = SetMsg.with_args(args_str)
        return AckAlarmMsg(alarm_msg) if alarm_msg else None

    def __str__(self):
        return 'RALM' + str(self.alarm_msg)[4:]

class PauseBipMsg:
    def __init__(self, duration_ms):
        self.duration_ms = duration_ms

    def with_args(args_str):
        # TODO: check we have a number
        return PauseBipMsg(int(args_str))

    def __str__(self):
        return 'PBIP %05d' % self.duration_ms

class PauseInsMsg:
    def __init__(self, duration_ms):
        self.duration_ms = duration_ms

    def with_args(args_str):
        # TODO: check we have a number
        return PauseInsMsg(int(args_str))

    def __str__(self):
        return 'PINS %03d' % self.duration_ms

class PauseExpMsg:
    def __init__(self, duration_ms):
        self.duration_ms = duration_ms

    def with_args(args_str):
        # TODO: check we have a number
        return PauseExpMsg(int(args_str))

    def __str__(self):
        return 'PEXP %03d' % self.duration_ms

def checksum8(frame):
    assert isinstance(frame, str)
    return sum(ord(c) for c in frame) % 256

checksum_pattern = re.compile(r'^\tCS8:([0-9a-fA-F]{2})\n$')

def parse_msg(msg_str):
    assert isinstance(msg_str, str)
    if len(msg_str) < 12: # minimum message length with id and checksum
        print("incomplete message", file=sys.stderr)
        return None

    # checksum
    match = re.search(checksum_pattern, msg_str[-8:])
    if not match:
        print("failed to parse checksum", msg_str[-8:], file=sys.stderr)
        return None
    checksum = int(match.group(1), 16)
    if checksum8(msg_str[:-3]) != checksum:
        print("wrong checksum", file=sys.stderr)
        return None

    id_ = msg_str[:4]
    ctors = {
        'DATA': DataMsg.with_args,
        'RESP': RespMsg.with_args,
        'SET_': SetMsg.with_args,
        'ALRM': AlarmMsg.with_args,
        'RALM': AckAlarmMsg.with_args,
        'PBIP': PauseBipMsg.with_args,
        'PINS': PauseInsMsg.with_args,
        'PEXP': PauseExpMsg.with_args,
        'INIT': InitMsg.with_args,
    }
    if id_ not in ctors:
        print("unknown message id:", id_, file=sys.stderr)
        return None
    return ctors[id_](msg_str[5:-8])

def serialize_msg(msg):
    msg_str = str(msg) + "\tCS8:"
    return msg_str + "%02X\n" % checksum8(msg_str)
