# -*- coding: utf-8 -*-
"""
.. module:: tests.test_binary_write
    :synopsis: Unit tests for binary formatter read/modify blocks possibility
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
import io
import allure
from udlg import enums
from udlg.builder import BinaryFormatterFileBuilder, UDLGBuilder
from unittest import TestCase


@allure.feature('Binary Writer')
class BinaryFormatterFileTest(TestCase):
    def setUp(self):
        self.string_file = open('tests/documents/string.dat', 'rb')
        self.lucas = open('tests/documents/Lucas1.udlg', 'rb')

    def tearDown(self):
        self.string_file.close()

    @allure.story('to bin')
    def test_header_to_bin(self):
        instance = BinaryFormatterFileBuilder.build(self.string_file)
        with allure.step('check'):
            self.assertEqual(instance.header.record_type,
                             enums.RecordTypeEnum.SerializedStreamHeader)
        with allure.step('to bin'):
            binary_data = instance.header.to_bin()
            self.assertIsInstance(binary_data, bytearray)
            self.assertEqual(len(binary_data), 17)

    @allure.story('to bin')
    def test_convert_to_bin(self):
        """
        convert back to binary format
        """
        instance = BinaryFormatterFileBuilder.build(self.string_file)
        with allure.step('check'):
            self.assertEqual(instance.header.record_type,
                             enums.RecordTypeEnum.SerializedStreamHeader)
        with allure.step('to bin'):
            binary_data = instance.to_bin()
            self.assertIsInstance(binary_data, bytearray)
            self.assertEqual(len(binary_data), 51)
        with allure.step('from bin'):
            stream = io.BytesIO(binary_data)
            instance_from = BinaryFormatterFileBuilder.build(stream=stream)
            self.assertEqual(instance.count, instance_from.count)

    @allure.story('to bin')
    def test_udlg_convert_to_bin(self):
        instance = UDLGBuilder.build(self.lucas)
        with allure.step('check'):
            self.assertEqual(instance.data.header.record_type,
                             enums.RecordTypeEnum.SerializedStreamHeader)
        with allure.step('to bin'):
            binary_data = instance.to_bin()
            self.assertIsInstance(binary_data, bytearray)
            self.assertEqual(len(binary_data), self.lucas.tell())
        with allure.step('from bin'):
            stream = io.BytesIO(binary_data)
            instance_from = UDLGBuilder.build(stream=stream)
            self.assertEqual(instance.data.count, instance_from.data.count)
