# -*- coding: utf-8 -*-
"""
.. module:: udlg.structure.base
    :synopsis: Base classes for structures
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from struct import unpack, calcsize
from ctypes import Structure, cast, pointer, c_void_p, _SimpleCData, _Pointer


class BinaryRecordStructure(Structure):
    def __repr__(self):
        return '<%s at 0x%08x>' % (self.__class__.__name__,
                                   id(self))

    def get_void_ptr(self):
        return cast(pointer(self), c_void_p)

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
        for field_name, field_type in self._fields_:
            if issubclass(field_type, self.__class__) or hasattr(field_type,
                                                                 '_initiate'):
                instance = field_type()
                instance._initiate(stream)
                setattr(self, field_name, instance)
            elif issubclass(field_type, _SimpleCData):
                field_format = field_type._type_
                field_size = calcsize(field_format)
                data_block, = unpack(field_format, stream.read(field_size))
                setattr(self, field_name, data_block)
            elif issubclass(field_type, _Pointer):
                #: nothing to do, should be initialized in subclass
                pass
            else:
                raise TypeError("Wrong field type: `%r`" % type(field_type))
