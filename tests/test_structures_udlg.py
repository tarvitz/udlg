# -*- coding: utf-8 -*-
"""
.. module:: tests.test_structures_udlg
    :synopsis: Unit test for structures are being used in *.udlg files
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
import allure
from udlg.structure.structure import SerializationHeader
from unittest import TestCase


@allure.feature('Structures')
class SerializationHeaderTest(TestCase):
    def setUp(self):
        self.stream = open('tests/documents/cc_dogInMotion.udlg', 'rb')
        self.stream2 = open('tests/documents/Lucas1.udlg', 'rb')

    def tearDown(self):
        self.stream.close()
        self.stream2.close()

    @allure.story('check two structure entities for their equality')
    def test_not_eq(self):
        with allure.step('check different files headers'):
            header = SerializationHeader()
            header_other = SerializationHeader()
            header._initiate(stream=self.stream)
            header_other._initiate(stream=self.stream2)
            self.assertNotEqual(header, header_other)
        with allure.step('check same file headers'):
            header = SerializationHeader()
            header_other = SerializationHeader()
            header._initiate(stream=self.stream, seek=0)
            header_other._initiate(stream=self.stream, seek=0)
            self.assertEqual(header, header_other)
