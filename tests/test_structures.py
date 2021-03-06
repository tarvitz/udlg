# -*- coding: utf-8 -*-
"""
.. module:: tests.test_structures
    :synopsis: Test structures
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
import allure
import ctypes
from ctypes import c_uint64, c_char_p, POINTER, pointer, c_void_p, cast
from unittest import TestCase

from udlg import enums


class Simple(ctypes.Structure):
    _fields_ = [
        ('length', ctypes.c_uint32),
        ('name', ctypes.c_char_p)
    ]

    def get_void_ptr(self):
        return cast(pointer(self), c_void_p)


class PStructure(ctypes.Structure):
    _fields_ = [
        ('a_length', c_uint64),
        ('p_field', POINTER(c_uint64))
    ]


class PAStructure(ctypes.Structure):
    _fields_ = [
        ('pa_length', c_uint64),
        ('pa_fields', POINTER(c_uint64))
    ]


class EnumInStructure(ctypes.Structure):
    _fields_ = [
        #: enums.RecordTypeEnum
        ('record_type', ctypes.c_ubyte)
    ]


class PointerOnStructure(ctypes.Structure):
    _fields_ = [
        ('record_type', ctypes.c_ubyte),
        ('entry', POINTER(Simple)),
        #: would point on anything
        ('super_entry', c_void_p)
    ]

    def set(self, value):
        if isinstance(value, str):
            value = value.encode('utf-8')
        self.entry.contents.name = value

    @property
    def entry(self):
        if not hasattr(self, '_entry'):
            if self.record_type == 0x1:
                self._entry = cast(self.super_entry, POINTER(Simple))
            else:
                raise TypeError("Wrong super entry pointer type")
        return self._entry


@allure.feature('Structures')
class PointerArrayInStructureTest(TestCase):
    def setUp(self):
        self.ia_storage = (c_uint64 * 3)(1, 2, 3)

    def test_ia_iter(self):
        """
        iterate through int array
        """
        for idx, item in enumerate(self.ia_storage, 1):
            self.assertEqual(item, idx)

    def test_pointer_on_uint64_in_structure(self):
        """
        using address math you can access items with python index operation.
        Python iter operation could case segfault (no stop for such kind of
        iteration so process would take until protected memory address would
        meet.
        """
        with allure.step('setup environment'):
            p = PStructure()
            p.a_length = len(self.ia_storage)
            p.p_field = self.ia_storage
        with allure.step('check address math'):
            for x in range(p.a_length):
                self.assertEqual(p.p_field[x], x + 1)


@allure.feature('Structures')
class EnumStructureTest(TestCase):
    def test_enum_in_structure(self):
        with allure.step('configure environment'):
            instance = EnumInStructure()
            instance.record_type = 10
        with allure.step('check'):
            self.assertEqual(instance.record_type, 10)
            self.assertEqual(instance.record_type,
                             enums.RecordTypeEnum.ObjectNull)


@allure.feature('Structures')
class VoidPointerInTest(TestCase):
    def setUp(self):
        self.entry = Simple()
        self.entry.name = ctypes.c_char_p(b'simple')
        self.entry.length = len(self.entry.name)
        self.super_entry = Simple()
        self.super_entry.name = ctypes.c_char_p(b'super entry')
        self.super_entry.length = len(self.super_entry.name)

    def test_void_pointer_in_structure(self):
        with allure.step('configure environment'):
            instance = PointerOnStructure()
            instance.record_type = 11
            instance.entry = pointer(self.entry)
            super_entry_ptr = pointer(self.super_entry)
            #: convert super_entry pointer to void pointer type
            void_ptr = cast(super_entry_ptr, c_void_p)
            #: write it down
            instance.super_entry = void_ptr
        with allure.step('check'):
            self.assertEqual(instance.entry.contents.name, b"simple")
            self.assertEqual(instance.entry.contents.length, 6)
            with allure.step('apply void ptr'):
                #: recast void pointer from structure to our pointer type
                super_entry = cast(instance.super_entry, POINTER(Simple))
                self.assertEqual(super_entry.contents.name, b'super entry')
                self.assertEqual(super_entry.contents.length, 11)


@allure.feature('Structures')
class OnFreeStringTest(TestCase):
    def setUp(self):
        value = b"some simple string here"
        self.simple = Simple(length=len(value), name=value)
        self.p_structure = PointerOnStructure(
            record_type=1, entry=pointer(self.simple),
            super_entry=self.simple.get_void_ptr()
        )

    def test_user_after_free(self):
        with allure.step('setup environment'):
            self.assertEqual(self.p_structure.entry.contents.name,
                             self.simple.name)
        with allure.step('reconfigure'):
            self.p_structure.entry.contents.name = c_char_p(b"some new data")
            self.assertEqual(self.p_structure.entry.contents.name,
                             b"some new data")
            value = c_char_p(b"new data")
            self.p_structure.entry.contents.name = value
            with allure.step('delete'):
                del value
        with allure.step('check'):
            self.assertEqual(self.p_structure.entry.contents.name,
                             b"new data")
        with allure.step('method set'):
            self.p_structure.set(u'юникот')
        with allure.step('check after method set'):
            self.assertEqual(self.p_structure.entry.contents.name,
                             'юникот'.encode('utf-8'))
