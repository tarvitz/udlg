# -*- coding: utf-8 -*-
"""
.. module:: udlg.structure.common
    :synopsis: Enumerations
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from __future__ import unicode_literals

import ctypes
from ctypes import c_int32, c_uint32, c_void_p, c_ubyte, cast, pointer, POINTER
from struct import unpack

from .base import BinaryRecordStructure
from .constants import (
    BinaryTypeEnum, PrimitiveTypeEnum, RecordTypeEnum,
    PrimitiveTypeCTypesConversionSet,
    AdditionalInfoTypeEnum,
    UINT32_SIZE, BYTE_SIZE, INT32_SIZE
)
from . import modules
from .. utils import read_7bit_encoded_int_from_stream
from .. import enums


class LengthPrefixedString(BinaryRecordStructure):
    _fields_ = [
        ('size', ctypes.c_uint32),
        ('value', ctypes.c_wchar_p)
    ]

    def __repr__(self):
        if self.value:
            return "'%s'" % self.value
        return repr(self)

    def __str__(self):
        if self.value:
            return self.value
        return '<LengthPrefixedString at 0x%16x>' % id(self)

    def __eq__(self, other):
        return self.value == other

    def __len__(self):
        return len(self.value)

    def __le__(self, other):
        return self.value <= other

    def __lt__(self, other):
        return self.value < other

    def __ge__(self, other):
        return self.value >= other

    def __gt__(self, other):
        return self.value > other

    def __ne__(self, other):
        return self.value != other

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
        size = read_7bit_encoded_int_from_stream(stream=stream)
        self.size = size
        self.value = ctypes.c_wchar_p(stream.read(size).decode('utf-8'))


class PrimitiveValue(ctypes.Structure):
    _fields_ = [
        ('primitive_type', BinaryTypeEnum),
        #: only value is significant
        ('value_ptr', c_void_p)
    ]


class ValueWithCode(ctypes.Structure):
    _fields_ = [
        ('type', PrimitiveTypeEnum),
        ('value', PrimitiveValue)
    ]


class StringValueWithCode(ctypes.Structure):
    _fields_ = [
        ('type', PrimitiveTypeEnum),
        ('value', LengthPrefixedString)
    ]


class ArrayOfValueWithCode(ctypes.Structure):
    _fields_ = [
        ('length', c_uint32),
        #: array
        ('values', POINTER(ValueWithCode))
    ]


class ArrayInfo(BinaryRecordStructure):
    _fields_ = [
        ('object_id', c_int32),
        ('length', c_uint32)
    ]


class ClassInfo(BinaryRecordStructure):
    _fields_ = [
        ('object_id', c_int32),
        ('name', LengthPrefixedString),
        ('members_count', c_uint32),
        ('members_names', POINTER(LengthPrefixedString))
    ]

    def _initiate(self, stream):
        self.object_id, = unpack('i', stream.read(INT32_SIZE))
        self.name = LengthPrefixedString()
        self.name._initiate(stream)
        self.members_count, = unpack('I', stream.read(UINT32_SIZE))
        member_names = []
        append = member_names.append
        for i in range(self.members_count):
            member = LengthPrefixedString()
            member._initiate(stream)
            append(member)
        names = (LengthPrefixedString * len(member_names))(*member_names)
        self.members_names = names


class ClassTypeInfo(BinaryRecordStructure):
    _fields_ = [
        ('type_name', LengthPrefixedString),
        ('library_id', c_uint32)
    ]


class BinaryEnumType(ctypes.Structure):
    _fields_ = [
        ('binary_type', BinaryTypeEnum)
    ]


class AdditionalInfo(BinaryRecordStructure):
    _fields_ = [
        ('type', AdditionalInfoTypeEnum),
        ('entry_ptr', c_void_p),
    ]

    @property
    def value(self):
        """
        extracts value, caches it and get it back

        :rtype: int | udlg.structure.common.ClassInfo |
            udlg.structure.common.LengthPrefixedString
        :return: value
        """
        if not hasattr(self, '_value') and self.entry_ptr:
            AdditionalInfoTypeEnum = enums.AdditionalInfoTypeEnum
            if self.type in (AdditionalInfoTypeEnum.PrimitiveTypeEnum,
                             AdditionalInfoTypeEnum.PrimitiveArrayTypeEnum):
                self._value = cast(
                    self.entry_ptr, POINTER(c_ubyte * 1)
                ).contents[0]
            elif self.type == AdditionalInfoTypeEnum.ClassInfo:
                self._value = cast(POINTER(ClassInfo), self.entry_ptr)
            elif self.type == AdditionalInfoTypeEnum.LengthPrefixedString:
                self._value = cast(POINTER(LengthPrefixedString),
                                   self.entry_ptr)
            else:
                raise TypeError(
                    "Wrong additional type format stored: %i" % self.type
                )
        elif not self.entry_ptr:
            return None
        return self._value

    def assign_entry(self, entry):
        """
        assigns entry according to self type and store it as entry void pointer
        (entry ptr)

        :param entry: permitted data to store
        :rtype: None
        :return: None
        """
        #: todo reconfigure
        if entry is None:
            return

        if self.type in (enums.AdditionalInfoTypeEnum.PrimitiveTypeEnum,
                         enums.AdditionalInfoTypeEnum.PrimitiveArrayTypeEnum):
            #: todo make it safe
            #: it's highly insecure as we assign byte itself not an address
            #: where it placed
            #: primitive type has byte info about primitive type
            entry_ptr = cast(pointer((c_ubyte * 1)(*(entry, ))), c_void_p)
            self.entry_ptr = entry_ptr
        elif self.type in (enums.AdditionalInfoTypeEnum.ClassTypeInfo,
                           enums.AdditionalInfoTypeEnum.LengthPrefixedString):
            self.entry_ptr = cast(pointer(entry), c_void_p)
        else:
            raise TypeError(
                "Given type `%r` of entry isn't supported" % type(entry)
            )


class MemberTypeInfo(BinaryRecordStructure):
    _fields_ = [
        ('types', POINTER(BinaryTypeEnum)),
        ('additional_info', POINTER(AdditionalInfo))
    ]

    def _initiate(self, stream, amount=0):
        """
        initiate member type info information

        :param stream: stream like object, file stream for example
        :param amount: amount of members should read from stream (this
            amount could be taken from ClassInfo instance)
        :rtype: None
        :return: None
        """
        # types and additional info are
        types = unpack('%ib' % amount, stream.read(amount))
        self.types = (BinaryTypeEnum * amount)(*types)
        additional_infoes = []
        append = additional_infoes.append

        for idx in range(amount):
            bin_type = self.types[idx]
            entry = None
            if bin_type == enums.BinaryTypeEnum.Primitive:
                entry, = unpack('b', stream.read(BYTE_SIZE))
                additional_info = AdditionalInfo(
                    type=enums.AdditionalInfoTypeEnum.PrimitiveTypeEnum
                )
            elif bin_type == enums.BinaryTypeEnum.PrimitiveArray:
                entry, = unpack('b', stream.read(BYTE_SIZE))
                additional_info = AdditionalInfo(
                    type=enums.AdditionalInfoTypeEnum.PrimitiveArrayTypeEnum
                )
            elif bin_type == enums.BinaryTypeEnum.Class:
                additional_info = AdditionalInfo(
                    type=enums.AdditionalInfoTypeEnum.ClassTypeInfo
                )
                entry = ClassTypeInfo()
                entry._initiate(stream)
            elif bin_type == enums.BinaryTypeEnum.SystemClass:
                additional_info = AdditionalInfo(
                    type=enums.AdditionalInfoTypeEnum.LengthPrefixedString
                )
                entry = LengthPrefixedString()
                entry._initiate(stream)
            else:
                additional_info = AdditionalInfo(
                    type=enums.AdditionalInfoTypeEnum.Null
                )
            additional_info.assign_entry(entry)
            append(additional_info)
        self.additional_info = (
            AdditionalInfo * len(additional_infoes)
        )(*additional_infoes)


class ObjectNull(BinaryRecordStructure):
    _fields_ = [
        ('record_type', RecordTypeEnum)
    ]


#: Member and MemberEntry does not include in official spec, it uses as
#: link to access member data with some structure that indent to have some
#: member list with different type of data
class MemberEntry(ctypes.Structure):
    """
    """
    _fields_ = (
        ('record_type', RecordTypeEnum),
        ('binary_type', BinaryTypeEnum),
        ('primitive_type', PrimitiveTypeEnum),
        ('member_ptr', c_void_p)
    )

    @property
    def member(self):
        if not hasattr(self, '_member'):
            #: conversion process
            binary_type = self.binary_type
            record_type = self.record_type
            if binary_type in (enums.BinaryTypeEnum.PrimitiveArray,
                               enums.BinaryTypeEnum.Primitive):
                member_type = PrimitiveTypeCTypesConversionSet[
                    self.primitive_type
                ]
                self._member = cast(
                    self.member_ptr, POINTER(member_type * 1)
                ).contents[0]
            elif record_type:
                record_class = getattr(
                    modules.RECORDS_MODULE,
                    enums.RecordTypeEnum(record_type).name
                )
                self._member = cast(
                    self.member_ptr, POINTER(record_class)
                ).contents
            else:
                raise NotImplementedError(
                    "Not implemented yet or wrong type"
                )
        return self._member


#: not used
class Members(ctypes.Structure):
    _fields_ = [
        ('members_count', ctypes.c_uint32),
        ('members', POINTER(MemberEntry))
    ]

    def get_list(self):
        """
        get python list of members

        :rtype: list
        :return: list of members
        """
        if not hasattr(self, '_members'):
            self._members = []
            append = self._members.append
            for i in range(self.members_count):
                append(self.members[i].member)
        return self._members


class AdditionalTypeInfo(ctypes.Structure):
    _fields_ = [
        ('binary_type', BinaryTypeEnum),
        ('value_ptr', c_void_p)
    ]

    @property
    def value(self):
        if not hasattr(self, '_value'):
            if self.binary_type in (enums.BinaryTypeEnum.Primitive,
                                    enums.BinaryTypeEnum.PrimitiveArray):
                self._value = cast(self.value_ptr,
                                   POINTER(c_uint32)).contents[0]
            elif self.binary_type == enums.BinaryTypeEnum.SystemClass:
                self._value = cast(self.value_ptr,
                                   POINTER(LengthPrefixedString)).contents
            elif self.binary_type == enums.BinaryTypeEnum.Class:
                self._value = cast(self.value_ptr,
                                   POINTER(ClassTypeInfo)).contents
            else:
                self._value = None
        return self._value
