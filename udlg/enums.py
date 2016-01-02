# -*- coding: utf-8 -*-
"""
.. module:: udlg.enums
    :synopsis: Enumerations
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from enum import IntEnum


class RecordTypeEnum(IntEnum):
    SerializedStreamHeader = 0,
    ClassWithId = 1,
    SystemClassWithMembers = 2,
    ClassWithMembers = 3,
    SystemClassWithMembersAndTypes = 4,
    ClassWithMembersAndTypes =5,
    BinaryObjectString = 6,
    BinaryArray = 7,
    MemberPrimitiveTyped = 8,
    MemberReference = 9,
    ObjectNull = 10,
    MessageEnd = 11,
    BinaryLibrary = 12,
    ObjectNullMultiple256 = 13,
    ObjectNullMultiple = 14,
    ArraySinglePrimitive = 15,
    ArraySingleObject = 16,
    ArraySingleString = 17,
    MethodCall = 21,
    MethodReturn = 22,
    BinaryMethodCall = 0

    @classmethod
    def get_member_values(cls):
        if not hasattr(cls, '_member_values'):
            cls._member_values = cls.__members__.values()
        return cls._member_values


class PrimitiveTypeEnum(IntEnum):
    Boolean = 1,
    Byte = 2,
    Char = 3,
    Decimal = 5,
    Double = 6,
    Int16 = 7,
    Int32 = 8,
    Int64 = 9,
    SByte = 10,
    Single = 11,
    TimeSpan = 12,
    DateTime = 13,
    UInt16 = 14,
    UInt32 = 15,
    UInt64 = 16,
    Null = 17,
    String = 18

    @classmethod
    def get_int_types(cls):
        return (
            cls.Int16, cls.Int32, cls.Int64, cls.UInt16, cls.UInt32, cls.UInt64
        )

    @classmethod
    def get_float_types(cls):
        return cls.Single, cls.Double

    @classmethod
    def get_invalid_types(cls):
        return cls.String, cls.Null


class BinaryTypeEnum(IntEnum):
    Primitive = 0,
    String = 1,
    Object = 2,
    SystemClass = 3,
    Class = 4,
    ObjectArray = 5,
    StringArray = 6,
    PrimitiveArray = 7


class BinaryArrayTypeEnum(IntEnum):
    Single = 0,
    Jagged = 1,
    Rectangular = 2,
    SingleOffset = 3,
    JaggedOffset = 4,
    RectangularOffset = 5

    @classmethod
    def get_lower_bounds(cls):
        return cls.SingleOffset, cls.JaggedOffset, cls.RectangularOffset

class MessageEnum(IntEnum):
    noArgs = 0x1,
    ArgsInline = 0x2,
    ArgsIsArray = 0x4,
    ArgsInArray = 0x8,
    NoContext = 0x10,
    ContextInline = 0x20,
    ContextInArray = 0x40,
    MethodSignatureInArray = 0x80,
    PropertiesInArray = 0x100,
    NoReturnValue = 0x200,
    ReturnValueVoid = 0x400,
    ReturnValueInline = 0x800,
    ReturnValueInArray = 0x1000,
    ExceptionInArray = 0x2000,
    GenericMethod = 0x8000


#: this enum is not part of .NET Binary Data structure, it uses for
#: data detection inside additional type
class AdditionalInfoTypeEnum(IntEnum):
    PrimitiveTypeEnum = BinaryTypeEnum.Primitive
    PrimitiveArrayTypeEnum = BinaryTypeEnum.PrimitiveArray
    ClassTypeInfo = BinaryTypeEnum.SystemClass
    LengthPrefixedString = BinaryTypeEnum.Class
    Null = -1
