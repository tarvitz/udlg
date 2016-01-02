# -*- coding: utf-8 -*-
"""
.. module:: udlg.structure.utils
    :synopsis: Utilities
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from struct import unpack, calcsize
from ctypes import resize, sizeof, addressof, cast, c_void_p
from . constants import (
    BYTE_SIZE, PrimitiveTypeConversionSet, PrimitiveTypeCTypesConversionSet

)
from ..enums import PrimitiveTypeEnum


def read_record_type(stream, seek_back=True):
    """
    reads record type

    :param stream: stream object, file for example
    :param bool seek_back: seek backwards after read block, True by default
        if False no any seek operation
    :rtype: udlg.structure.constants.RecordTypeEnum
    :return: record type
    """
    record_type, = unpack('b', stream.read(BYTE_SIZE))
    if seek_back:
        stream.seek(-1, 1)
    return record_type


def resize_array(array, size):
    """
    extends array with given size

    :param array: ctypes array
    :param int size: new size (should be more than current size)
    :return: pointer on new array
    """
    resize(array, sizeof(array._type_) * size)
    return (array._type_ * size).from_address(addressof(array))


#: todo implement timespan, decimal, datetime
def read_primitive_type_from_stream(stream, type):
    """
    read primitive type from stream

    :param stream: stream object, for example file stream
    :param int type: type (PrimitiveTypeEnumeration based type)
    :rtype: int | float | bool | datetime | char | decimal.Decimal
    :return:
    """
    call_format = PrimitiveTypeConversionSet[type]
    call_size = calcsize(call_format)
    value, = unpack(call_format, stream.read(call_size))
    return value


def make_primitive_type_elements_array_pointer(type, elements):
    """
    create void pointer on array elements

    :param PrimitiveTypeEnum type: primitive type
    :param list | tuple elements: primitive type elements (values)
    :rtype: ctypes.c_void_p
    :return: void pointer on array
    """
    size = len(elements)
    array_type = PrimitiveTypeCTypesConversionSet[type]
    array = (array_type * size)(*elements)
    return cast(array, c_void_p)
