# -*- coding: utf-8 -*-
"""
.. module:: udlg.structure.modules
    :synopsis: Modules
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""

import importlib
from .constants import RECORDS_MODULE_PATH

RECORDS_MODULE = importlib.import_module(RECORDS_MODULE_PATH)
