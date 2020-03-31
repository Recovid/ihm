#!/usr/bin/python

import re
import sys

class TimeData:
    def __init__(self, timestamp_ms, volume_ml, debit_lpm, paw_mbar):
        self.timestamp_ms = timestamp_ms
        self.volume_ml = volume_ml
        self.debit_lpm = debit_lpm
        self.paw_mbar = paw_mbar

class InputData:
    def __init__(self, fio2_pct, vt_ml, fr_pm, pep_mbar, pip_mbar, pplat_mbar):
        self.fio2_pct = fio2_pct
        self.vt_ml = vt_ml
        self.fr_pm = fr_pm
        self.pep_mbar = pep_mbar
        self.pip_mbar = pip_mbar
        self.pplat_mbar = pplat_mbar

class DataMsg:
    args_pattern = re.compile('^msec:(\d{5}) Vol__:(\d{4}) Deb__:([+-]\d{3}) Paw__:([+-]\d{3})( Fi02_:(\d{3}) Vt___:(\d{4}) FR___:(\d{2}) PEP__:(\d{2}) PIP__:(\d{3}) PPLAT:(\d{3}))?')

    def __init__(self, time_data, input_data=None):
        self.time_data = time_data
        self.input_data = input_data

    def with_args(args_str):
        match = re.match(DataMsg.args_pattern, args_str)
        if not match:
            print("failed to parse DATA message", file=sys.stderr)
            return None
        time_data = TimeData(*[int(g) for g in match.groups()[0:4]])
        input_data = InputData(*[int(g) for g in match.groups()[5:11]]) if match.group(5) else None
        return DataMsg(time_data, input_data)

    def __str__(self):
        d = self.time_data
        args = (d.timestamp_ms % 100000, d.volume_ml, '-' if d.debit_lpm < 0 else '+', d.debit_lpm, '-' if d.paw_mbar < 0 else '+', abs(d.paw_mbar))
        s = 'DATA msec:%05d Vol__:%04d Deb__:%s%03d Paw__:%s%03d' % args
        if self.input_data:
            d = self.input_data
            args = (d.fio2_pct, d.vt_ml, d.fr_pm, d.pep_mbar, d.pip_mbar, d.pplat_mbar)
            s += ' Fi02_:%03d Vt___:%04d FR___:%02d PEP__:%02d PIP__:%03d PPLAT:%03d' % args
        return s

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
        return AlarmMsg(args_str[1:-1])

    def __str__(self):
        return 'ALRM \'%s\'' % (self.setting, self.value)

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

def checksum8(frame):
    assert isinstance(frame, str)
    return sum(ord(c) for c in frame) % 256

checksum_pattern = re.compile(r'^ CS8_:([0-9a-fA-F]{2})\n$')

def parse_msg(msg_str):
    assert isinstance(msg_str, str)
    if len(msg_str) < 12: # minimum message length with id and checksum
        print("incomplete message", file=sys.stderr)
        return None

    # checksum
    match = re.search(checksum_pattern, msg_str[-9:])
    if not match:
        print("failed to parse checksum", file=sys.stderr)
        return None
    checksum = int(match.group(1), 16)
    if checksum8(msg_str[:-3]) != checksum:
        print("wrong checksum", file=sys.stderr)
        return None

    id_ = msg_str[:4]
    ctors = {
        'DATA': DataMsg.with_args,
        'SET_': SetMsg.with_args,
        'RSET': AckSetMsg.with_args,
        'ALRM': AlarmMsg.with_args,
        'RALM': AckAlarmMsg.with_args,
    }
    if id_ not in ctors:
        print("unknown message id", file=sys.stderr)
        return None
    return ctors[id_](msg_str[5:])

def checked_msg(msg):
    msg += " CS8_:"
    return msg + "%02X\n" % checksum8(msg)

def serialize_msg(msg):
    msg_str = str(msg) + " CS8_:"
    return msg_str + "%02X\n" % checksum8(msg_str)
