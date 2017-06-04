#!/usr/bin/env python3.4

import denonavr_serial
import unittest


SERIAL_PORT = '/dev/ttyUSB0'
d = denonavr_serial.Avr3805(SERIAL_PORT)
d.power_on()
d.main.power_off()


# Tests that are common to main and other zones
class DenonCommonTest(object):
    def require_power_on(self):
        if not self.denon.powered_on():
            self.denon.power_on()

    def test_power_state_on(self):
        self.assertTrue(self.denon.powered_on())

    def test_volume_set(self):
        self.require_power_on()
        for level in [0.5, 1.0, 0.0]:
            self.denon.set_volume(level)
            self.assertAlmostEqual(self.denon.get_volume(), level)

    def test_volume_relative_adjust(self):
        self.require_power_on()
        self.denon.set_volume(0.5)
        default = self.denon.get_volume()
        self.assertAlmostEqual(self.denon.get_volume(), 0.5)

        self.denon.volume_down()
        l = self.denon.get_volume()
        self.assertLess(l, default)

        self.denon.volume_up()
        self.denon.volume_up()
        h = self.denon.get_volume()
        self.assertGreater(h, default)

        self.assertAlmostEquals(h - default, default - l)

    def test_get_source(self):
        self.require_power_on()
        src = self.denon.get_source()
        self.assertIn(src, d.sources)

    def test_set_source(self):
        self.require_power_on()
        for src in d.sources:
            self.denon.set_source(src)
            self.assertEqual(src, self.denon.get_source())

    def test_switch_source_after_power_on(self):
        src1 = d.sources[0]
        src2 = d.sources[1]

        self.denon.set_source(src1)
        self.assertEqual(src1, self.denon.get_source())

        self.denon.power_off()
        self.assertFalse(self.denon.powered_on())

        self.denon.power_on()
        self.assertTrue(self.denon.powered_on())

        self.denon.set_source(src2)
        self.assertEqual(src2, self.denon.get_source())


# Tests that are unique to the main zone
class DenonMainTest(DenonCommonTest, unittest.TestCase):
    def setUp(self):
        self.denon = d.main

    def test_mute(self):
        self.require_power_on()
        self.denon.mute()
        self.assertTrue(self.denon.muted())
        self.denon.unmute()
        self.assertFalse(self.denon.muted())


# Tests for a non-main zone
class DenonZoneTest(DenonCommonTest, unittest.TestCase):
    def setUp(self):
        # TODO: This will break for receivers without 2 zones
        self.denon = d.zone[1]
