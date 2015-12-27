# -*- coding: utf-8 -*-
"""
.. module:: tests.test_udlg
    :synopsis: Unit tests for UDLG format
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
import allure
from udlg import UDLG, UDLGBuilder
from unittest import TestCase


@allure.feature('UDLG')
class UDLGTest(TestCase):
    def setUp(self):
        self.stream = open('tests/documents/cc_dogInMotion.udlg', 'rb')

    def tearDown(self):
        self.stream.close()

    @allure.story('start block')
    def test_read_start_block(self):
        udlg = UDLGBuilder.build(stream=self.stream)
        self.assertEqual(len(udlg.start.spaces), 3)

    @allure.story('header block')
    def test_read_header_block(self):
        udlg = UDLGBuilder.build(stream=self.stream)
        self.assertEqual(udlg.header.length, 2)
        self.assertEqual(udlg.header.entry_amount, 11)
        with allure.step('check header entries'):
            for i in range(udlg.header.entry_amount):
                entry = udlg.header.entries[i]
                self.assertGreater(entry.length, 0)
                self.assertEqual(len(entry.signature), entry.length)

    @allure.story('header block')
    def test_header_block_len(self):
        udlg = UDLGBuilder.build(stream=self.stream)

        with allure.step('check header entries length'):
            sizes = [len(udlg.header.entries[i]) for i in range(11)]
            self.assertEqual(sum(sizes), 93)

        self.assertEqual(len(udlg.header), 101)
