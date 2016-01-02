# -*- coding: utf-8 -*-
"""
.. module:: udlg.structure
    :synopsis: UDLG format structures
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from __future__ import unicode_literals

import importlib
import ctypes
from struct import unpack
from ctypes import (
    c_uint32, c_uint64, c_int32, c_byte, c_ubyte, c_char_p,
    POINTER, sizeof, cast,
)
from .constants import (
    BYTE_SIZE, INT_SIZE, RecordTypeEnum, RECORDS_MODULE_PATH
)
from .utils import read_record_type
from .. import enums

SAFE_SIZES = [
    c_uint64, c_byte, c_uint32
]
RECORDS_MODULE = importlib.import_module(RECORDS_MODULE_PATH)


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


class SerializationHeader(ctypes.Structure):
    _fields_ = [
        #: enums.RecordTypeEnum
        ('record_type', c_ubyte),
        ('root_id', c_int32),
        ('header_id', c_int32),
        ('major_version', c_int32),
        ('minor_version', c_int32)
    ]

    def _initiate(self, stream):
        """
        initiate instance fields (construct) from stream

        .. warning::

            Stream offset should be set up right on block that identifies
            as Serialization Header

        :param stream: stream object, file stream for example
        :rtype: None
        :return: None
        """
        stream.seek(0)
        record_type, = unpack('b', stream.read(BYTE_SIZE))
        root_id, header_id, major_version, minor_version = unpack(
            '4i', stream.read(INT_SIZE * 4)
        )
        self.record_type = record_type
        self.root_id = root_id
        self.header_id = header_id
        self.major_version = major_version
        self.minor_version = minor_version


class Record(ctypes.Structure):
    _fields_ = (
        ('record_type', RecordTypeEnum),
        ('entry_ptr', ctypes.c_void_p)
    )

    def __init__(self, *args, **kwargs):
        self._entry = None
        super(Record, self).__init__(*args, **kwargs)

    @property
    def entry(self):
        """
        resolve entry

        :rtype: ctypes.Structure
        :return: one of valid .net binary data structure instances
        """
        if not hasattr(self, '_entry'):
            record_type = self.record_type
            RecordType = enums.RecordTypeEnum
            class_name = RecordType(record_type).name
            record_class = getattr(RECORDS_MODULE, class_name, self.__class__)
            pointer_type = POINTER(record_class)
            self._entry = cast(self.entry_ptr, pointer_type).contents
        return self._entry

    def _initiate(self, stream):
        """
        initiate instance fields (construct) from stream

        .. warning::

            Stream offset should be set up right on block that identifies
            as Serialization Header

        :param stream: stream object, file stream for example
        :rtype: None
        :return: None
        """
        self.record_type = read_record_type(stream)
        record_class_name = enums.RecordTypeEnum(self.record_type).name
        record_entry_class = getattr(RECORDS_MODULE, record_class_name)
        record_entry = record_entry_class()
        record_entry._initiate(stream)
        entry_void_ptr = record_entry.get_void_ptr()
        self.entry_ptr = entry_void_ptr


class BinaryDataStructureFile(ctypes.Structure):
    _fields_ = [
        ('header', SerializationHeader),
        ('records', POINTER(Record))
    ]
