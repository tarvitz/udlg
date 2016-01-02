# -*- coding: utf-8 -*-
"""
.. module:: udlg.structure.constants
    :synopsis: Constants, aliases
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""

from ctypes import (
    c_byte, c_ubyte, c_uint32, c_float, c_double, c_int16, c_int32, c_int64,
    c_uint16, c_uint32, c_uint64, c_bool, c_char
)
from .. enums import PrimitiveTypeEnum as PrimitiveTypeEnumeration

#: some records unified location
RECORDS_MODULE_PATH = 'udlg.structure.records'

#: enums
RecordTypeEnum = c_ubyte
PrimitiveTypeEnum = c_ubyte
BinaryTypeEnum = c_ubyte
AdditionalInfoTypeEnum = c_ubyte
BinaryArrayTypeEnum = c_ubyte

#: in bytes
BYTE_SIZE = 1
INT_SIZE = 4
UINT_SIZE = 4
UINT32_SIZE = 4
UINT64_SIZE = 8

#: conversions
#: key -> function handling primitive type
PrimitiveTypeConversionSet = {
    PrimitiveTypeEnumeration.Boolean: '?',
    PrimitiveTypeEnumeration.Byte: 'B',  #: unsigned byte
    PrimitiveTypeEnumeration.Char: 'c',
    #: would raise TypeError as it should be implemented
    #: decimal should be read as LengthPrefixedString yet ;\
    PrimitiveTypeEnumeration.Decimal: None,
    PrimitiveTypeEnumeration.Double: 'd',
    PrimitiveTypeEnumeration.Int16: 'h',
    PrimitiveTypeEnumeration.Int32: 'i',
    PrimitiveTypeEnumeration.Int64: 'q',
    PrimitiveTypeEnumeration.UInt16: 'H',
    PrimitiveTypeEnumeration.UInt32: 'I',
    PrimitiveTypeEnumeration.UInt64: 'Q',
    PrimitiveTypeEnumeration.SByte: 'b',
    PrimitiveTypeEnumeration.Single: 'f',
    PrimitiveTypeEnumeration.TimeSpan: 'q',
    PrimitiveTypeEnumeration.DateTime: 'Q',
    #: this part is forbidden to use in conversions so it's ok
    PrimitiveTypeEnumeration.Null: None,
    PrimitiveTypeEnumeration.String: None
}

PrimitiveTypeCTypesConversionSet = {
    PrimitiveTypeEnumeration.Boolean: c_bool,
    PrimitiveTypeEnumeration.Byte: c_ubyte,  #: unsigned byte
    PrimitiveTypeEnumeration.Char: c_char,
    #: would raise TypeError as it should be implemented
    #: decimal should be read as LengthPrefixedString yet ;\
    PrimitiveTypeEnumeration.Decimal: None,
    PrimitiveTypeEnumeration.Double: c_double,
    PrimitiveTypeEnumeration.Int16: c_int16,
    PrimitiveTypeEnumeration.Int32: c_int32,
    PrimitiveTypeEnumeration.Int64: c_int64,
    PrimitiveTypeEnumeration.UInt16: c_uint16,
    PrimitiveTypeEnumeration.UInt32: c_uint32,
    PrimitiveTypeEnumeration.UInt64: c_uint64,
    PrimitiveTypeEnumeration.SByte: c_byte,
    PrimitiveTypeEnumeration.Single: c_float,
    PrimitiveTypeEnumeration.TimeSpan: c_int64,
    PrimitiveTypeEnumeration.DateTime: c_uint64,
    #: this part is forbidden to use in conversions so it's ok
    PrimitiveTypeEnumeration.Null: None,
    PrimitiveTypeEnumeration.String: None
}
