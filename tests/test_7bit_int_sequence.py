# -*- coding: utf-8 -*-
"""
.. module:: tests.test_7bit_int_sequence
    :synopsis: https://en.wikipedia.org/wiki/Variable-length_quantity
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
import io
import allure
from udlg.utils import (
    read_7bit_encoded_int, read_7bit_encoded_int_from_stream, write_7bit_int)
from unittest import TestCase


@allure.feature('')
class StringLengthTest(TestCase):
    def setUp(self):
        self.map = {
            '10': b'\x0a',
            '127': b'\x7f',
            '128': b'\x80\x01',
            '256': b'\x80\x02',
            '384': b'\x80\x03',
            '390': b'\x86\x03'
        }
        self.stream = io.BytesIO(b'\x86\x03')

    def test_read_7bit_int(self):
        """
        iterate through int array
        """
        for key, src in self.map.items():
            self.assertTrue(int(key), read_7bit_encoded_int(src))

    def test_7bit_from_stream(self):
        self.assertEqual(read_7bit_encoded_int_from_stream(self.stream), 390)

    def test_write_7bit_int(self):
        errors = []
        for key, value in self.map.items():
            try:
                self.assertEqual(self.map[key], write_7bit_int(int(key)))
            except AssertionError as e:
                errors.append({
                    'value': key,
                    'error': e
                })
        if errors:
            raise AssertionError(errors)
