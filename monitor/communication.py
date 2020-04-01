#!/usr/bin/python

import re
import sys

class DataMsg:
    args_pattern = re.compile('^msec_:(\d{5}) Vol__:(\d{4}) Deb__:([+-]\d{3}) Paw__:([+-]\d{3})$')

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
        args = (self.timestamp_ms % 100000, self.volume_ml, '-' if self.debit_lpm < 0 else '+', self.debit_lpm, '-' if self.paw_mbar < 0 else '+', abs(self.paw_mbar))
        return 'DATA msec_:%05d Vol__:%04d Deb__:%s%03d Paw__:%s%03d' % args

class RespMsg:
    args_pattern = re.compile('^Fi02_:(\d{3}) Vt___:(\d{4}) FR___:(\d{2}) PEP__:(\d{2}) PIP__:(\d{3}) PPLAT:(\d{3})$')

    def __init__(self, fio2_pct, vt_ml, fr_pm, pep_mbar, pip_mbar, pplat_mbar):
        self.fio2_pct = fio2_pct
        self.vt_ml = vt_ml
        self.fr_pm = fr_pm
        self.pep_mbar = pep_mbar
        self.pip_mbar = pip_mbar
        self.pplat_mbar = pplat_mbar

    def with_args(args_str):
        match = re.match(RespMsg.args_pattern, args_str)
        if not match:
            print("failed to parse RESP message", file=sys.stderr)
            return None
        return RespMsg(*[int(g) for g in match.groups()[0:6]])

    def __str__(self):
        args = (self.fio2_pct, self.vt_ml, self.fr_pm, self.pep_mbar, self.pip_mbar, self.pplat_mbar)
        return 'RESP Fi02_:%03d Vt___:%04d FR___:%02d PEP__:%02d PIP__:%03d PPLAT:%03d' % args

class SetMsg:
    args_pattern = re.compile('^(\w{5}):(\d{2,5})$')

    def __init__(self, setting, value):
        self.setting = setting
        self.value = value

    def with_args(args_str):
        match = re.match(SetMsg.args_pattern, args_str)
        if not match:
            print("failed to parse SET_ message", file=sys.stderr)
            return None
        # TODO: check setting is valid
        return SetMsg(match.group(1), int(match.group(2)))

    def __str__(self):
        # TODO: fixed number of digits
        return 'SET_ %s:%d' % (self.setting, self.value)

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

class AckSetMsg:
    def __init__(self, set_msg):
        self.set_msg = set_msg

    def with_args(args_str):
        set_msg = SetMsg.with_args(args_str)
        return AckSetMsg(set_msg) if set_msg else None

class AckAlarmMsg:
    def __init__(self, alarm_msg):
        self.alarm_msg = alarm_msg

    def with_args(args_str):
        alarm_msg = SetMsg.with_args(args_str)
        return AckSetMsg(alarm_msg) if alarm_msg else None

class BeepMsg:
    args_pattern = re.compile('^dur__:(\d{5})$')

    def __init__(self, duration_ms):
        self.duration_ms = setting

    def with_args(args_str):
        match = re.match(BeepMsg.args_pattern, args_str)
        if not match:
            print("failed to parse BEEP message", file=sys.stderr)
            return None
        return BeepMsg(int(match.group(1)))

    def __str__(self):
        return 'BEEP dur__:%05d' % self.duration_ms

class PauseInsMsg:
    def __init__(self, duration_s):
        self.duration_s = setting

    def with_args(args_str):
        # TODO: check we have a number
        return PauseInsMsg(int(args_str))

    def __str__(self):
        return 'PINS %02d' % self.duration_s

class PauseExpMsg:
    def __init__(self, duration_s):
        self.duration_s = setting

    def with_args(args_str):
        # TODO: check we have a number
        return PauseExpMsg(int(args_str))

    def __str__(self):
        return 'PEXP %02d' % self.duration_s

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
        'RSET': AckSetMsg.with_args,
        'ALRM': AlarmMsg.with_args,
        'RALM': AckAlarmMsg.with_args,
        'BEEP': BeepMsg.with_args,
        'PINS': PauseInsMsg.with_args,
        'PEXP': PauseExpMsg.with_args,
        'INIT': InitMsg.with_args,
    }
    if id_ not in ctors:
        print("unknown message id", file=sys.stderr)
        return None
    return ctors[id_](msg_str[5:-8])

def serialize_msg(msg):
    msg_str = str(msg) + "\tCS8:"
    return msg_str + "%02X\n" % checksum8(msg_str)
