# -*- coding: utf-8 -*-
"""
.. module:: tests.test_binary_formatter
    :synopsis: Unit tests for .NET Binary Format Data structure
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
import allure
from udlg import enums
from udlg.builder import BinaryFormatterFileBuilder
from udlg.structure import records
from unittest import TestCase

#: todo make test check if stream is open as binary one


@allure.feature('Binary Formatter')
class BinaryFormatterFileTest(TestCase):
    def setUp(self):
        self.string_file = open('tests/documents/string.dat', 'rb')
        self.uint32_file = open('tests/documents/uint32.dat', 'rb')
        self.string_array_file = open('tests/documents/string_array.dat', 'rb')
        self.uint32_array_file = open('tests/documents/uint32_array.dat', 'rb')
        self.ushort_array_file = open('tests/documents/ushort_array.dat', 'rb')
        self.bool_array_file = open('tests/documents/bool_array.dat', 'rb')
        self.double_array_file = open('tests/documents/double_array.dat', 'rb')
        self.class_instance_file = open(
            'tests/documents/simpleclass.dat', 'rb'
        )
        self.class_with_id_file = open(
            'tests/documents/class_with_id.dat', 'rb'
        )

    def tearDown(self):
        self.string_file.close()
        self.uint32_file.close()
        self.string_array_file.close()
        self.uint32_array_file.close()
        self.ushort_array_file.close()
        self.bool_array_file.close()
        self.double_array_file.close()
        self.class_instance_file.close()
        self.class_with_id_file.close()

    @allure.story('string')
    def test_header(self):
        instance = BinaryFormatterFileBuilder.build(self.string_file)
        with allure.step('check'):
            self.assertEqual(instance.header.record_type,
                             enums.RecordTypeEnum.SerializedStreamHeader)
            self.assertEqual(instance.header.root_id, 1)
            self.assertEqual(instance.header.header_id, -1)
            self.assertEqual(instance.header.major_version, 1)
            self.assertEqual(instance.header.minor_version, 0)

    @allure.story('string')
    def test_string(self):
        instance = BinaryFormatterFileBuilder.build(stream=self.string_file)
        with allure.step('check records'):
            self.assertEqual(instance.records[0].entry.value.value,
                             'String should be serialized')
            self.assertIsInstance(instance.records[1].entry,
                                  records.MessageEnd)

    @allure.story('int')
    def test_int32(self):
        instance = BinaryFormatterFileBuilder.build(stream=self.uint32_file)
        with allure.step('check records'):
            self.assertEqual(instance.records[0].entry.member_list, [1337])
            with allure.step('check members like python list'):
                self.assertEqual(
                    instance.records[0].entry.get_member_list(), [1337]
                )
            self.assertIsInstance(instance.records[1].entry,
                                  records.MessageEnd)

    @allure.story('string')
    def test_string_array(self):
        instance = BinaryFormatterFileBuilder.build(
            stream=self.string_array_file
        )
        with allure.step('check array single string'):
            self.assertIsInstance(
                instance.records[0].entry, records.ArraySingleString
            )
        with allure.step('check records'):
            self.assertIsInstance(
                instance.records[1].entry, records.BinaryObjectString
            )
            entry = instance.records[1].entry
            self.assertEqual(entry.value.value, "bla")
            entry = instance.records[256].entry
            self.assertEqual(entry.value.value, 'Z' * 130)
        with allure.step('check message end'):
            self.assertIsInstance(instance.records[257].entry,
                                  records.MessageEnd)

    @allure.story('int')
    def test_uint32_array(self):
        instance = BinaryFormatterFileBuilder.build(
            stream=self.uint32_array_file
        )
        with allure.step('check array single string'):
            self.assertIsInstance(
                instance.records[0].entry, records.ArraySinglePrimitive
            )
        with allure.step('check records'):
            self.assertEqual(
                instance.records[0].entry.get_member_list(),
                [1337, 1338, 1339, 7331, 7332, 7333, 7334, 7335, 7336, 7337,
                 7338, 7338, 7339, 1111, 1231, 3, 2]
            )
        with allure.step('check message end'):
            self.assertIsInstance(instance.records[1].entry,
                                  records.MessageEnd)

    @allure.story('short')
    def test_ushort_array(self):
        instance = BinaryFormatterFileBuilder.build(
            stream=self.ushort_array_file
        )
        with allure.step('check array single string'):
            self.assertIsInstance(
                instance.records[0].entry, records.ArraySinglePrimitive
            )
        with allure.step('check records'):
            self.assertEqual(
                instance.records[0].entry.get_member_list(),
                [1337, 1338, 1339, 7331, 7332, 7333, 7334, 7335, 7336, 7337,
                 7338, 7338, 7339, 1111, 1231]
            )
        with allure.step('check message end'):
            self.assertIsInstance(instance.records[1].entry,
                                  records.MessageEnd)

    @allure.story('double')
    def test_double_array(self):
        instance = BinaryFormatterFileBuilder.build(
            stream=self.double_array_file
        )
        with allure.step('check array single string'):
            self.assertIsInstance(
                instance.records[0].entry, records.ArraySinglePrimitive
            )
        with allure.step('check records'):
            self.assertEqual(
                instance.records[0].entry.get_member_list(),
                [1337.0, 1338.0, 1339.0, 7331.0, -7332.35009765625,
                 -7333.0, 7334.0, 7335.0, 7336.0, 7337.0, 7338.0,
                 7338.0, 7339.0, 1111.0, 1231.0, 3.123199939727783,
                 -2.3299999237060547]
            )
        with allure.step('check message end'):
            self.assertIsInstance(instance.records[1].entry,
                                  records.MessageEnd)

    @allure.story('bool')
    def test_bool_array(self):
        instance = BinaryFormatterFileBuilder.build(
            stream=self.bool_array_file
        )
        with allure.step('check array single string'):
            self.assertIsInstance(
                instance.records[0].entry, records.ArraySinglePrimitive
            )
        with allure.step('check records'):
            self.assertEqual(
                instance.records[0].entry.get_member_list(),
                [True, False, False, True, False, False, False, True, True,
                 True, True, False, False, False, True, True, False]
            )
        with allure.step('check message end'):
            self.assertIsInstance(instance.records[1].entry,
                                  records.MessageEnd)

    @allure.story('class')
    def test_class_instance(self):
        instance = BinaryFormatterFileBuilder.build(
            stream=self.class_instance_file
        )
        with allure.step('check first record'):
            self.assertIsInstance(
                instance.records[0].entry, records.BinaryLibrary
            )
        with allure.step('check class with members and types'):
            entry = instance.records[1].entry
            self.assertIsInstance(entry, records.ClassWithMembersAndTypes)
            self.assertEqual(entry.class_info.members_count, 15)
            self.assertEqual(entry.member_list[0].value.value, 'blast')
            self.assertIsInstance(entry.member_list[1],
                                  records.MemberReference)
            self.assertIsInstance(entry.member_list[2],
                                  records.MemberReference)
            self.assertIsInstance(entry.member_list[3],
                                  records.ObjectNull)
            self.assertIsInstance(entry.member_list[4],
                                  records.ObjectNull)
            self.assertIsInstance(entry.member_list[5],
                                  records.BinaryObjectString)
            self.assertIsInstance(entry.member_list[6],
                                  records.BinaryObjectString)
            self.assertEqual(entry.member_list[7], 0x74)
            self.assertIsInstance(instance.records[14].entry,
                                  records.ArraySinglePrimitive)
            self.assertEqual(instance.records[14].entry.get_member_list(),
                             [100, 200, 300, 400, 500, 600, 700, 800, 900,
                              1000, 1100, 1200, 1300])
        with allure.step('check message end'):
            self.assertIsInstance(instance.records[15].entry,
                                  records.MessageEnd)

    @allure.story('class')
    def test_class_with_id(self):
        instance = BinaryFormatterFileBuilder.build(
            stream=self.class_with_id_file
        )
        with allure.step('check first record'):
            self.assertIsInstance(
                instance.records[0].entry, records.BinaryLibrary
            )
        with allure.step('check '):
            self.assertIsInstance(
                instance.records[15].entry, records.ClassWithId
            )
            entry = instance.records[15].entry
            member_types = [records.BinaryObjectString, int, bool]
            member_values = ["bla-bla-fier", 1340, True]
            for member, member_type, member_value in zip(
                    entry.get_member_list(), member_types, member_values):
                self.assertIsInstance(member, member_type)
                self.assertEqual(member, member_value)
        with allure.step('check message end'):
            self.assertIsInstance(
                instance.records[22].entry, records.MessageEnd
            )
