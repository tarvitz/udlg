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
from ctypes import c_uint64, POINTER
from unittest import TestCase


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


@allure.feature('PO')
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
