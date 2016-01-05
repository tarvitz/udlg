# -*- coding: utf-8 -*-
"""
.. module:: udlg.utils.i18n
    :synopsis: i18n tools
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from collections import defaultdict
import re

FLAGS = re.S | re.M | re.I | re.U
I18N_REG = re.compile(
    r"(?P<record_id>\d+),(?P<member_id>\d+)=>(?P<content>(?:''|'.+?'))$",
    FLAGS
)


def get_i18n_items(block):
    """
    prepare i18n items from i18n file like object

    :param bytes block: block to parse
    :rtype: dict
    :return: i18n items
    """
    storage = defaultdict(dict)
    items = re.findall(I18N_REG, block.decode('utf-8'))
    for (record_idx, member_idx, message) in items:
        storage[int(record_idx)][int(member_idx)] = (
            message[1:-1]
        )
    return storage
