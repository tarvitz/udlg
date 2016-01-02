# -*- coding: utf-8 -*-
"""
.. module:: udlg.structure.records
    :synopsis: .NET Binary Data structure records:

        - BinaryObjectString
        - MessageEnd
        - SystemClassWithMembersAndTypes
        - ArraySingleString
        - ArraySinglePrimitive
        - ObjectNull
        - MemberReference
        - BinaryLibrary
        - BinaryArray
        - ClassWithMembersAndTypes
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""

from __future__ import unicode_literals

from struct import unpack, calcsize
from ctypes import c_uint32, c_void_p, c_ubyte, cast, pointer, POINTER

from .base import BinaryRecordStructure
from .constants import (
    RecordTypeEnum, PrimitiveTypeEnum, BinaryTypeEnum, BinaryArrayTypeEnum,
    BYTE_SIZE, UINT32_SIZE,
    PrimitiveTypeCTypesConversionSet, PrimitiveTypeConversionSet,
)
from .common import (
    LengthPrefixedString, ClassInfo, MemberTypeInfo, MemberEntry, ArrayInfo,
    AdditionalTypeInfo, ClassTypeInfo
)
from .utils import (
    read_record_type,
    read_primitive_type_from_stream,
    make_primitive_type_elements_array_pointer)
from .. import enums


class MessageEnd(BinaryRecordStructure):
    _fields_ = [
        ('record_type', RecordTypeEnum)
    ]


class BinaryObjectString(BinaryRecordStructure):
    _fields_ = [
        ('record_type', RecordTypeEnum),
        ('object_id', c_uint32),
        ('value', LengthPrefixedString)
    ]


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
                append(self._create_member_entry(value, additional_info,
                                                 member_type))
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

    def _create_member_entry(self, value, additional_info, member_type):
        """
        initiate member entry with specific type

        :param BinaryTypeEnum type: binary type
        :param value: data to store
        :rtype: MemberEntry
        :return: member entry
        """
        primitive_type = 0
        if member_type in (enums.BinaryTypeEnum.Primitive,
                           enums.BinaryTypeEnum.PrimitiveArray):
            primitive_type = enums.PrimitiveTypeEnum(additional_info.value)
            array_type = PrimitiveTypeCTypesConversionSet[primitive_type]
            value_entry = (array_type * 1)(*(value, ))
            member_ptr = cast(pointer(value_entry), c_void_p)
        else:
            member_ptr = value.get_void_ptr()
        member_entry = MemberEntry(
            type=member_type, primitive_type=primitive_type,
            member_ptr=member_ptr
        )
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


class BinaryLibrary(BinaryRecordStructure):
    _fields_ = [
        ('record_type', RecordTypeEnum),
        ('library_id', c_uint32),
        ('library_name', LengthPrefixedString)
    ]


class ClassWithMembersAndTypes(BinaryRecordStructure):
    _fields_ = [
        ('record_type', RecordTypeEnum),
        ('class_info', ClassInfo),
        ('member_type_info', MemberTypeInfo),
        ('library_id', c_uint32),
        ('members_ptr', POINTER(MemberEntry)),
    ]

    def _initiate(self, stream):
        self.record_type, = unpack('b', stream.read(BYTE_SIZE))
        self.class_info = ClassInfo()
        self.class_info._initiate(stream)
        self.member_type_info = MemberTypeInfo()
        self.member_type_info._initiate(
            stream, amount=self.class_info.members_count
        )
        self.library_id, = unpack('I', stream.read(UINT32_SIZE))
        self._initiate_members(stream)

    def _initiate_members(self, stream):
        """
        initiate members

        :param stream: stream like object, file stream for example
        :return: None
        """
        members_count = self.class_info.members_count
        members = []
        append = members.append
        binary_types = self.member_type_info.types
        additional_infoes = self.member_type_info.additional_info

        for i in range(self.class_info.members_count):
            binary_type = binary_types[i]
            additional_info = additional_infoes[i]

            if binary_type == enums.BinaryTypeEnum.Primitive:
                member_entry = MemberEntry(
                    type=binary_type, primitive_type=additional_info.value
                )
                entry_ctype = PrimitiveTypeCTypesConversionSet[
                    additional_info.value
                ]
                primitive_type_format = PrimitiveTypeConversionSet[
                    enums.PrimitiveTypeEnum(additional_info.value)
                ]
                primitive_type_size = calcsize(primitive_type_format)
                value, = unpack(primitive_type_format,
                                stream.read(primitive_type_size))
                array_size = 1
                value_array = (entry_ctype * array_size)(*(value, ))
                member_entry.member_ptr = cast(pointer(value_array), c_void_p)
            else:
                record_type = read_record_type(stream)
                member_record_class = globals()[
                    enums.RecordTypeEnum(record_type).name
                ]
                member_record = member_record_class()
                member_record._initiate(stream)
                member_entry = MemberEntry(
                    binary_type=binary_type, primitive_type=0,
                    record_type=record_type,
                    member_ptr=member_record.get_void_ptr()
                )
            append(member_entry)
        members_array = (MemberEntry * members_count)(*members)
        self.members_ptr = members_array

    def get_member_list(self):
        """
        get member python list

        :rtype: list
        :return: member list
        """
        if not hasattr(self, '_members'):
            self._members = []
            append = self._members.append
            member_entries = cast(
                self.members_ptr, POINTER(MemberEntry)
            )
            for i in range(self.class_info.members_count):
                append(member_entries[i].member)
        return self._members

    @property
    def member_list(self):
        return self.get_member_list()


class MemberReference(BinaryRecordStructure):
    _fields_ = [
        ('record_type', RecordTypeEnum),
        ('id_ref', c_uint32)
    ]


class ObjectNull(BinaryRecordStructure):
    _fields_ = [
        ('record_type', RecordTypeEnum)
    ]


class BinaryArray(BinaryRecordStructure):
    _fields_ = [
        ('record_type', RecordTypeEnum),
        ('object_id', c_uint32),
        ('binary_type', BinaryArrayTypeEnum),
        ('rank', c_uint32),
        ('lengths', POINTER(c_uint32)),
        ('lower_bounds', POINTER(c_uint32)),
        ('type', BinaryTypeEnum),
        ('additional_type_info', AdditionalTypeInfo)
    ]

    def _initiate(self, stream):
        self.record_type, = unpack('b', stream.read(BYTE_SIZE))
        self.object_id, = unpack('I', stream.read(UINT32_SIZE))
        self.binary_type, = unpack('b', stream.read(BYTE_SIZE))
        self.rank, = unpack('I', stream.read(UINT32_SIZE))
        lengths = unpack(
            '%iI' % self.rank, stream.read(UINT32_SIZE * self.rank)
        )
        self.lengths = (c_uint32 * len(lengths))(*lengths)
        if self.binary_type in (enums.BinaryArrayTypeEnum.get_lower_bounds()):
            lower_bounds = unpack(
                '%iI' % self.rank, stream.read(UINT32_SIZE * self.rank)
            )
            self.lower_bounds = (c_uint32 * len(lower_bounds))(*lower_bounds)
        self.type, = unpack('b', stream.read(BYTE_SIZE))
        additional_type_info = AdditionalTypeInfo(binary_type=self.type)
        if self.type in (enums.BinaryTypeEnum.Primitive,
                         enums.BinaryTypeEnum.PrimitiveArray):
            primitive_type, = unpack('b', stream.read(BYTE_SIZE))
            value = (c_uint32 * 1)(*(primitive_type, ))
            value_ptr = cast(pointer(value), c_void_p)
            additional_type_info.value_ptr = value_ptr
        elif self.type == enums.BinaryTypeEnum.SystemClass:
            value = LengthPrefixedString()
            value._initiate(stream)
            additional_type_info.value_ptr = value.get_void_ptr()
        elif self.type == enums.BinaryTypeEnum.Class:
            value = ClassTypeInfo()
            value._initiate(stream)
            additional_type_info.value_ptr = value.get_void_ptr()
        else:
            raise TypeError("Wrong binary array type: %i" % self.type)
        self.additional_type_info = additional_type_info


class ClassWithId(BinaryRecordStructure):
    _fields_ = [
        ('record_type', RecordTypeEnum),
        ('object_id', c_uint32),
        ('metadata_id', c_uint32),
        ('member_ptr', c_void_p)
    ]

    def _initiate(self, stream):
        pass
