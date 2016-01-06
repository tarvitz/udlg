# -*- coding: utf-8 -*-
"""
.. module:: tests.test_udlg
    :synopsis: Unit test for *.udlg files
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
import io
import sys
import allure
from udlg import enums
from udlg.builder import UDLGBuilder
from udlg.structure import records
from unittest import TestCase


@allure.feature('UDLG')
class UDLGFileTest(TestCase):
    def setUp(self):
        self.cc_dog_in_motion = open('tests/documents/cc_dogInMotion.udlg',
                                     'rb')
        self.lucas = open('tests/documents/Lucas1.udlg', 'rb')
        self.lucas_i18n = open('tests/documents/Lucas1.txt', 'r')

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

    @allure.story('string modify')
    def test_length_prefixed_string_modify(self):
        instance = UDLGBuilder.build(self.lucas)
        with allure.step('modify string'):
            entry_1 = instance.data.records[5].members[2]
            entry_1.set("::Another:: string to set. Юникод")
            entry_2 = instance.data.records[6].members[3]
            entry_2.set('::Another:: set string (=. И Юникод')
        with allure.step('check'):
            #: still binary object string
            self.assertIsInstance(entry_1, records.BinaryObjectString)
            self.assertEqual(
                entry_1.value,
                "::Another:: string to set. Юникод".encode('utf-8')
            )
            self.assertIsInstance(entry_2, records.BinaryObjectString)
            self.assertEqual(
                entry_2.value,
                '::Another:: set string (=. И Юникод'.encode('utf-8')
            )
            instance_from = UDLGBuilder.build(io.BytesIO(instance.to_bin()))
            entry_1 = instance_from.data.records[5].members[2]
            entry_2 = instance_from.data.records[6].members[3]
            self.assertEqual(
                entry_1, "::Another:: string to set. Юникод".encode('utf-8')
            )
            self.assertEqual(
                entry_2, '::Another:: set string (=. И Юникод'.encode('utf-8')
            )

    @allure.story('i18n')
    def test_load_i18n(self):
        instance = UDLGBuilder.build(self.lucas)
        with allure.step('write i18n'):
            block = self.lucas_i18n.read().encode(sys.getfilesystemencoding())
            instance.load_i18n(block)
            with allure.step('check'):
                self.assertEqual(
                    instance.data.records[30].members[3],
                    u"::I:: gotta go actually. "
                    u"(d6012f9c-fe53-48b6-bffb-b20d10ff86bc)".encode('utf-8')
                )
                self.assertEqual(
                    instance.data.records[30].members[7],
                    u'::Fuck:: Что за чёрт? Пойду я отсюда. '
                    u'go-go-go.'.encode('utf-8')
                )
        with allure.step('check it once more'):
            stream = io.BytesIO(instance.to_bin())
            instance = UDLGBuilder.build(stream=stream)
            self.assertEqual(
                instance.data.records[30].members[3],
                u"::I:: gotta go actually. "
                u"(d6012f9c-fe53-48b6-bffb-b20d10ff86bc)".encode('utf-8')
            )
            self.assertEqual(
                instance.data.records[30].members[7],
                u'::Fuck:: Что за чёрт? Пойду я отсюда. '
                u'go-go-go.'.encode('utf-8')
            )
