#!/usr/bin/env python3.4

import serial
from datetime import datetime


DENON_SOURCE_PHONO = "PHONO"
DENON_SOURCE_CD = "CD"
DENON_SOURCE_TUNER = "TUNER"
DENON_SOURCE_DVD = "DVD"
DENON_SOURCE_VDP = "VDP"
DENON_SOURCE_TV = "TV"
DENON_SOURCE_DBS = "DBS/SAT"
DENON_SOURCE_VCR1 = "VCR-1"
DENON_SOURCE_VCR2 = "VCR-2"
DENON_SOURCE_VCR3 = "VCR-3"
DENON_SOURCE_VAUX = "V.AUX"
DENON_SOURCE_CDR_TAPE1 = "CDR/TAPE1"
DENON_SOURCE_MD_TAPE2 = "MD/TAPE2"


class Denon(object):
    def __init__(self, port, sources=[], zones=[]):
        self.serial = serial.Serial(port=port, baudrate=9600)
        self.main = DenonMain(self)
        self.zone = [DenonZone(self, zone) for zone in zones]
        self.sources = sources

    def _command(self, cmd, lines=1, timeout=0.3):
        cmd += '\r'
        cmd = cmd.encode('ascii')

        # drain input buffer prior to writing
        self.serial.read(self.serial.inWaiting())

        self.serial.write(cmd)
        self.serial.flush()

        buf = b''
        t1 = datetime.now()
        while buf.count(b'\r') != lines:
            buf += self.serial.read(self.serial.inWaiting())
            total_time = (datetime.now() - t1).total_seconds()
            if (total_time > timeout):
                break

        lines = buf.decode('ascii').split('\r')[:lines]
        return lines

    def _query(self, cmd, timeout=0.3):
        r = self._command(cmd, lines=1, timeout=timeout)
        return r[0]

    def _validate_source(self, source):
        if source not in self.sources:
            raise ValueError('invalid source: ' + str(source))

    def power_on(self):
        if not self.powered_on():
            self._command("PWON")

    def power_off(self):
        if self.powered_on():
            self._command("PWSTANDBY")

    def powered_on(self):
        resp = self._query("PW?")
        return resp == 'PWON'


class DenonMain(object):
    def __init__(self, denon):
        self.denon = denon

    def power_on(self):
        if not self.powered_on():
            self.denon._command('ZMON')

    def power_off(self):
        if self.powered_on():
            self.denon._command('ZMOFF')

    def powered_on(self):
        return 'ON' in self.denon._query('ZM?')

    def volume_up(self):
        self.denon._command('MVUP')

    def volume_down(self):
        self.denon._command('MVDOWN')

    def mute(self):
        self.denon._command('MUON')

    def unmute(self):
        self.denon._command('MUOFF')

    def muted(self):
        return 'ON' in self.denon._query('MU?')

    def get_volume(self):
        vol = self.denon._query('MV?', timeout=1.0)
        assert vol[:2] == 'MV'
        vol = vol[2:]
        if vol == '99':
            return 0.0
        db = float(vol)
        if len(vol) == 3:
            db /= 10.0
        db -= 80
        assert db <= 16.0 and db >= -80.0
        return (db + 80.0) / 96.0

    def set_volume(self, level):
        """Set volume to level between 0 and 1.0"""
        def convert_volume(level):
            if level < 0.0 or level > 1.0:
                raise ValueError('volume out of range [0, 1.0]: ' + str(level))
            assert level >= 0.0 and level <= 1.0
            db = round((level * 96.0 - 80.0) * 2) / 2
            denon_level = int((db + 80) * 10)
            if denon_level % 10:
                return "{:03d}".format(denon_level)
            else:
                return "{:02d}".format(int(denon_level / 10))

        if abs(level - self.get_volume()) < 0.001:
            return

        self.denon._command("MV" + convert_volume(level))

    def set_source(self, source):
        self.denon._validate_source(source)
        if source == self.get_source():
            return
        self.denon._command('SI' + source, lines=15, timeout=1.0)

    def get_source(self):
        source = self.denon._command('SI?', lines=15, timeout=0.5)[0]
        assert source[:2] == 'SI'
        source = source[2:]
        assert source in self.denon.sources
        return source


class DenonZone(object):
    def __init__(self, denon, zone):
        self.denon = denon
        self.zone = zone

    def _query(self):
        return self.denon._command(self.zone + '?', lines=3)

    def _command(self, cmd):
        self.denon._command(self.zone + cmd)

    def power_on(self):
        if not self.powered_on():
            self._command('ON')

    def power_off(self):
        if self.powered_on():
            self._command('OFF')

    def powered_on(self):
        return (self.zone + 'ON') in self._query()

    def volume_up(self):
        self._command('UP')

    def volume_down(self):
        self._command('DOWN')

    def set_volume(self, level):
        if level < 0.0 or level > 1.0:
            raise ValueError('volume out of range [0, 1.0]: ' + str(level))
        self._command("{:02d}".format(int(level * 98)))

    def get_volume(self):
        vol = int(self._query()[1][2:])
        if vol == 99:
            vol = 0
        return vol / 98.0

    def get_source(self):
        # TODO: Assuming that this always comes back in the same order
        source = self._query()[0][2:]
        assert source in self.denon.sources
        return source

    def set_source(self, source):
        self.denon._validate_source(source)
        if source == self.get_source():
            return
        self.denon._command(self.zone + source)


class Avr3805(Denon):
    def __init__(self, port):
        zones = ['Z1', 'Z2']
        sources = [DENON_SOURCE_PHONO, DENON_SOURCE_CD, DENON_SOURCE_TUNER,
                   DENON_SOURCE_DVD, DENON_SOURCE_VDP, DENON_SOURCE_TV,
                   DENON_SOURCE_DBS, DENON_SOURCE_VCR1, DENON_SOURCE_VCR2,
                   DENON_SOURCE_VAUX, DENON_SOURCE_CDR_TAPE1]

        super().__init__(port=port, zones=zones, sources=sources)


class Avc3890(Denon):
    def __init__(self, port):
        zones = ['Z1', 'Z2']
        sources = [DENON_SOURCE_PHONO, DENON_SOURCE_CD, DENON_SOURCE_TUNER,
                   DENON_SOURCE_DVD, DENON_SOURCE_VDP, DENON_SOURCE_TV,
                   DENON_SOURCE_DBS, DENON_SOURCE_VCR1, DENON_SOURCE_VCR2,
                   DENON_SOURCE_VCR3, DENON_SOURCE_VAUX,
                   DENON_SOURCE_CDR_TAPE1, DENON_SOURCE_MD_TAPE2]

        super().__init__(port=port, zones=zones, sources=sources)
