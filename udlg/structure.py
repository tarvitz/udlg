# -*- coding: utf-8 -*-
"""
.. module:: udlg.structure
    :synopsis: UDLG format structures
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from __future__ import unicode_literals

import ctypes
from struct import unpack
from ctypes import c_uint32, c_uint64, c_byte, c_char_p, POINTER, sizeof


SAFE_SIZES = [
    c_uint64, c_byte, c_uint32
]


def safe_size_of(c_type):
    return c_type in SAFE_SIZES and sizeof(c_type) or 0


class HeaderEntry(ctypes.Structure):
    _fields_ = [
        ('length', c_byte),
        ('signature', c_char_p),
        ('data', c_byte)
    ]
    _fields_map = dict(_fields_)

    def __len__(self):
        if not hasattr(self, '_length'):
            meta_size = sum(map(safe_size_of, self._fields_map.values()))
            self._length = meta_size + self.length
        return self._length
pHeaderEntry = POINTER(HeaderEntry)
StartBlockSpaces = (c_uint64 * 3)


class Header(ctypes.Structure):
    _start_offset = 0x34
    _fields_ = [
        ('zero', c_byte),
        ('length', c_byte),
        ('signature', c_char_p),
        ('entry_amount', c_uint32),
        ('entries', pHeaderEntry)
    ]

    def __iter__(self):
        for i in range(self.entry_amount):
            yield self.entries[i]

    def __len__(self):
        """
        header length

        :rtype: int
        :return: header length
        """

        #: the size if fixed no need to calculate it more than once
        if hasattr(self, '_length'):
            return self._length

        #: auto calculate size for safe files
        length = 0
        for field_name, field_type in self._fields_:
            if field_type in SAFE_SIZES:
                length += sizeof(field_type)
        length += self.length

        #: increase length according to its entries amount
        for i in range(self.entry_amount):
            length += len(self.entries[i])

        self._length = length
        return self._length

    def _initiate(self, stream):
        """
        read start block

        :param stream: stream object
        :rtype: None
        """
        pos = stream.tell()
        stream.seek(self._start_offset)
        _read = stream.read
        _read(1)
        self.length, = unpack('B', _read(1))
        self.signature = _read(self.length)
        self.entry_amount, = unpack('I', _read(4))
        #: read entries
        entries = []
        append = entries.append
        for i in range(self.entry_amount):
            entry = HeaderEntry()
            entry.length, = unpack('B', _read(1))
            entry.signature = _read(entry.length)
            append(entry)
        a_entries = (HeaderEntry * self.entry_amount)(*entries)
        self.entries = a_entries
        #: read entries some data
        for i in range(self.entry_amount):
            self.entries[i].data, = unpack('B', _read(1))
        stream.seek(pos)


class StartBlock(ctypes.Structure):
    _start_offset = 0x0
    _fields_ = [
        ("signature", c_char_p),
        ('identifier', c_uint64),
        ('spaces', StartBlockSpaces),
        ('block_index', c_uint32)
    ]

    def _initiate(self, stream):
        """
        read start block

        :param stream: stream object
        :rtype: None
        """
        pos = stream.tell()
        stream.seek(self._start_offset)
        _read = stream.read
        self.signature = _read(16)
        self.identifier, = unpack('Q', _read(8))
        self.spaces_amount = 3
        spaces = unpack('QQQ', _read(24))
        self.spaces = StartBlockSpaces(*spaces)
        stream.seek(pos)


class UDLG(ctypes.Structure):
    _fields_ = [
        ('start', StartBlock),
        ('header', Header)
    ]
