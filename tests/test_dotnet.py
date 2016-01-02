# -*- coding: utf-8 -*-
"""
.. module:: tests.test_dotnet
    :synopsis: Some dot net algos
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
import io
import allure
from udlg.utils import read_7bit_encoded_int, read_7bit_encoded_int_from_stream
from unittest import TestCase


@allure.feature('')
class StringLengthTest(TestCase):
    def setUp(self):
        self.map = {
            '10':  b'\x0a',
            '127': b'\x7f',
            '128': b'\x80\x01',
            '256': b'\x80\x02',
            '384': b'\x80\x03',
            '390': b'\x86\x03'
        }
        self.stream = io.BytesIO(b'\x86\x03')

    def test_7bit(self):
        """
        iterate through int array
        """
        for key, src in self.map.items():
            self.assertTrue(int(key), read_7bit_encoded_int(src))

    def test_7bit_from_stream(self):
        self.assertEqual(read_7bit_encoded_int_from_stream(self.stream), 390)
