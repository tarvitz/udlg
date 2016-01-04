# -*- coding: utf-8 -*-
"""
.. module:: tests.test_udlg
    :synopsis: Unit test for *.udlg files
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
import allure
from udlg import enums
from udlg.builder import UDLGBuilder
from udlg.structure import records
from unittest import TestCase


@allure.feature('UDLG')
class BinaryFormatterFileTest(TestCase):
    def setUp(self):
        self.cc_dog_in_motion = open('tests/documents/cc_dogInMotion.udlg',
                                     'rb')
        self.lucas = open('tests/documents/Lucas1.udlg', 'rb')

    def tearDown(self):
        self.cc_dog_in_motion.close()
        self.lucas.close()

    @allure.story('udlg')
    def test_cc_dog_in_motion(self):
        instance = UDLGBuilder.build(self.cc_dog_in_motion)
        with allure.step('check .net binary data format header'):
            net = instance.data
            self.assertEqual(net.header.record_type,
                             enums.RecordTypeEnum.SerializedStreamHeader)
            self.assertEqual(net.header.root_id, 1)
            self.assertEqual(net.header.header_id, -1)
            self.assertEqual(net.header.major_version, 1)
            self.assertEqual(net.header.minor_version, 0)
        with allure.step('check records consistency'):
            self.assertEqual(instance.data.count, 7)
            self.assertIsInstance(instance.data.records[0].entry,
                                  records.BinaryLibrary)
            self.assertIsInstance(instance.data.records[6].entry,
                                  records.MessageEnd)

    @allure.story('udlg')
    def test_lucas(self):
        instance = UDLGBuilder.build(self.lucas)
        with allure.step('check records'):
            self.assertEqual(instance.data.count, 96)
