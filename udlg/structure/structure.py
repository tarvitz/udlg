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
from ctypes import (
    c_uint32, c_uint64, c_int32, c_byte, c_ubyte,
    POINTER, sizeof, cast,
)
from .constants import (
    BYTE_SIZE, INT_SIZE, RecordTypeEnum
)
from . import records
from .utils import read_record_type
from .. import enums

SAFE_SIZES = [
    c_uint64, c_byte, c_uint32
]
SIGNATURE_SIZE = 24


def safe_size_of(c_type):
    return c_type in SAFE_SIZES and sizeof(c_type) or 0


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

    def __str__(self):
        return '<Record: at 0x%16x>' % id(self)

    def __repr__(self):
        if self.record_type:
            return repr(self.entry)
        return self.__str__()

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
            record_class = getattr(records, class_name, self.__class__)
            pointer_type = POINTER(record_class)
            self._entry = cast(self.entry_ptr, pointer_type).contents
        return self._entry

    def _initiate(self, stream, object_id_map):
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
        record_entry_class = getattr(records, record_class_name)
        record_entry = record_entry_class()
        record_entry._object_id_map = object_id_map
        record_entry._initiate(stream)

        #: todo make it fixed
        self._update_object_id_map(record_entry, object_id_map)

        entry_void_ptr = record_entry.get_void_ptr()
        self.entry_ptr = entry_void_ptr

    def _update_object_id_map(self, entry, object_id_map):
        """

        :param entry:
        :return:
        """
        #: todo something that should be reassemble
        if isinstance(entry, (records.ClassWithMembersAndTypes,
                              records.SystemClassWithMembersAndTypes)):
            object_id_map.update({
                entry.class_info.object_id: (
                    entry.record_type,
                    entry.get_void_ptr()
                )
            })
        elif isinstance(entry, (records.BinaryArray,
                                records.BinaryObjectString)):
            object_id_map.update({
                entry.object_id: (entry.record_type, entry.get_void_ptr())
            })
        else:
            pass


class UDLGHeader(ctypes.Structure):
    _fields_ = [
        ('signature', (c_byte * SIGNATURE_SIZE))
    ]


class BinaryDataStructureFile(ctypes.Structure):
    _fields_ = [
        ('header', SerializationHeader),
        ('records', POINTER(Record)),
        ('count', c_uint32)
    ]


class UDLGFile(ctypes.Structure):
    _fields_ = [
        ('header', UDLGHeader),
        ('data', BinaryDataStructureFile)
    ]

    def _initiate(self, stream):
        header = UDLGHeader()
        signature = unpack('%ib' % SIGNATURE_SIZE, stream.read(SIGNATURE_SIZE))
        header.signature = (c_byte * SIGNATURE_SIZE)(*signature)
        self.header = header
