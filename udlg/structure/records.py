# -*- coding: utf-8 -*-
"""
.. module:: udlg.structure.records
    :synopsis: .NET Binary Data structure records:

        - BinaryObjectString
        - MessageEnd
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""

from __future__ import unicode_literals

from struct import unpack
from ctypes import c_uint32, c_void_p, cast, pointer, POINTER

from .base import BinaryRecordStructure
from .constants import (
    RecordTypeEnum, PrimitiveTypeEnum, BYTE_SIZE, UINT32_SIZE,
    PrimitiveTypeCTypesConversionSet
)
from .common import (
    LengthPrefixedString, ClassInfo, MemberTypeInfo, MemberEntry, ArrayInfo,
    PrimitiveValue
)
from .utils import (
    read_primitive_type_from_stream, make_primitive_type_elements_array_pointer)
from .. import enums


class MessageEnd(BinaryRecordStructure):
    _fields_ = [
        ('record_type', RecordTypeEnum)
    ]

    def _initiate(self, stream):
        record_type, = unpack('b', stream.read(BYTE_SIZE))
        self.record_type = record_type


class BinaryObjectString(BinaryRecordStructure):
    _fields_ = [
        ('record_type', RecordTypeEnum),
        ('object_id', c_uint32),
        ('value', LengthPrefixedString)
    ]

    def _initiate(self, stream):
        self.record_type, = unpack('b', stream.read(BYTE_SIZE))
        self.object_id, = unpack('I', stream.read(UINT32_SIZE))
        #: todo think if make initiate not protected
        self.value._initiate(stream)


class SystemClassWithMembersAndTypes(BinaryRecordStructure):
    _fields_ = [
        ('record_type', RecordTypeEnum),
        ('class_info', ClassInfo),
        ('member_type_info', MemberTypeInfo),
        ('members', POINTER(MemberEntry)),
    ]

    def _initiate(self, stream):
        self.record_type, = unpack('b', stream.read(BYTE_SIZE))
        self.class_info = ClassInfo()
        self.class_info._initiate(stream)
        members_count = self.class_info.members_count
        self.member_type_info = MemberTypeInfo()
        self.member_type_info._initiate(stream, amount=members_count)
        self._initiate_members_data(stream)

    def _initiate_members_data(self, stream):
        """
        initiate member data that should follow right after header

        :param stream: stream like object, file stream for example
        :rtype: None
        :return: None
        """
        #: read members into self.members
        members_count = self.class_info.members_count
        # append = self.members.append
        AdditionalInfoTypeEnum = enums.AdditionalInfoTypeEnum
        is_primitive_type = AdditionalInfoTypeEnum.PrimitiveArrayTypeEnum
        is_primitive_array_type = (
            AdditionalInfoTypeEnum.PrimitiveTypeEnum
        )
        #: todo would be nice to iterate it pythonic way
        member_list = []
        append = member_list.append
        for i in range(members_count):
            member_type = self.member_type_info.types[i]
            #: todo additional info should be converted in desired format
            if member_type in (is_primitive_type, is_primitive_array_type):
                additional_info = self.member_type_info.additional_info[i]
                primitive_type = additional_info.value
                value = read_primitive_type_from_stream(stream, primitive_type)
                append(self._create_member_entry(member_type, value))
            elif member_type == AdditionalInfoTypeEnum.ClassInfo:
                raise NotImplementedError("Not implemented")
            elif member_type == AdditionalInfoTypeEnum.LengthPrefixedString:
                raise NotImplementedError("Not implemented")
            else:
                raise TypeError(
                    "Wrong type for members were given: %i" % member_type
                )
        #: assign members
        self.members = (MemberEntry * len(member_list))(*member_list)

    def _create_member_entry(self, type, value):
        """
        initiate member entry with specific type

        :param BinaryTypeEnum type: binary type
        :param value: data to store
        :rtype: MemberEntry
        :return: member entry
        """
        if type in (enums.BinaryTypeEnum.Primitive,
                    enums.BinaryTypeEnum.PrimitiveArray):
            member_ptr = c_void_p(value)
        else:
            member_ptr = value.get_void_ptr()
        member_entry = MemberEntry(type=type, member_ptr=member_ptr)
        return member_entry

    def get_member_list(self):
        """
        extracts members data and convert it into python list one

        :rtype: list
        :return: member list
        """
        if not hasattr(self, '_members'):
            self._members = []
            append = self._members.append
            for i in range(self.class_info.members_count):
                append(self.members[i].member)
        return self._members

    @property
    def member_list(self):
        return self.get_member_list()


class ArraySingleString(BinaryRecordStructure):
    _fields_ = [
        ('record_type', RecordTypeEnum),
        ('array_info', ArrayInfo)
    ]

    def _initiate(self, stream):
        self.record_type, = unpack('b', stream.read(BYTE_SIZE))
        self.array_info = ArrayInfo()
        self.array_info._initiate(stream)


class ArraySinglePrimitive(BinaryRecordStructure):
    _fields_ = [
        ('record_type', RecordTypeEnum),
        ('array_info', ArrayInfo),
        ('primitive_type', PrimitiveTypeEnum),
        ('members_ptr', c_void_p)
    ]

    def _initiate(self, stream):
        self.record_type, = unpack('b', stream.read(BYTE_SIZE))
        self.array_info = ArrayInfo()
        self.array_info._initiate(stream)
        self.primitive_type, = unpack('b', stream.read(BYTE_SIZE))
        elements = []
        append = elements.append
        for i in range(self.array_info.length):
            value = read_primitive_type_from_stream(
                stream, self.primitive_type
            )
            append(value)
        members_array_pointer = make_primitive_type_elements_array_pointer(
            self.primitive_type, elements
        )
        self.members_ptr = members_array_pointer

    def get_ctype_member_elements(self):
        """
        get ctype member elements

        :rtype: fixed size array of elements, for example c_double
        :return: ctype member elements
        """
        if not hasattr(self, '_ctype_elements'):
            array_type = PrimitiveTypeCTypesConversionSet[self.primitive_type]
            self._ctype_elements = cast(
                self.members_ptr, POINTER(array_type * self.array_info.length)
            ).contents
        return self._ctype_elements

    def get_member_list(self):
        """
        get member list in python format

        :rtype: list
        :return: member list
        """
        if not hasattr(self, '_members'):
            elements = self.get_ctype_member_elements()
            self._members = elements[:]
        return self._members
