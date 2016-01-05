# -*- coding: utf-8 -*-
"""
.. module:: tests.test_i18n
    :synopsis: Test i18n related issues
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from __future__ import unicode_literals

import sys
import allure
from unittest import TestCase
from udlg.utils.i18n import get_i18n_items


@allure.feature('i18n')
class I18nTest(TestCase):
    def setUp(self):
        self.i18n = open('tests/documents/i18n.txt', 'r')

    def tearDown(self):
        self.i18n.close()

    @allure.story('i18n')
    def test_load_i18n(self):
        block = self.i18n.read().encode(sys.getfilesystemencoding())
        items = get_i18n_items(block)
        self.assertIsInstance(items, dict)
        self.assertEqual(len(items), 4)
        self.assertEqual(set(items), {1, 5, 6, 91})
        self.assertEqual(items[91][3], "Тут немного юникода")
