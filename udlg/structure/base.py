# -*- coding: utf-8 -*-
"""
.. module:: udlg.structure.base
    :synopsis: Base classes for structures
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from struct import unpack, pack, calcsize
from ctypes import Structure, cast, pointer, c_void_p, _SimpleCData, _Pointer
from .constants import PrimitiveTypeConversionSet

class SimpleSerializerMixin(object):
    """
    Very basic and dumb serializer :), please do not count on it too much.
    """
    def to_dict(self):
        document = {}
        for field_name, field_type in self._fields_:
            entry = getattr(self, field_name.replace('_ptr', ''))
            if isinstance(entry, list):
                value = [
                    x.to_dict() if hasattr(x, 'to_dict') else x for x in entry
                ]
            else:
                value = entry.to_dict() if hasattr(entry, 'to_dict') else entry
            document.update({
                field_name.replace('_ptr', ''): value
            })
        return document

    def to_bin(self):
        """
        convert python to byte

        :rtype: bytearray
        :return: binary data
        """
        document = bytearray()
        extend = document.extend

        #: super extra hack
        member_type_info = None
        if hasattr(self, 'member_type_info'):
            member_type_info = self.member_type_info
        elif hasattr(self, 'class_reference'):
            member_type_info = self.class_reference.member_type_info
        else:
            pass

        for field_name, field_type in self._fields_:
            #: some data should not be serialized
            if field_name in getattr(self, '_exclude_', []):
                continue

            entry = getattr(self, field_name.replace('_ptr', ''))
            if hasattr(entry, 'to_bin'):
                extend(entry.to_bin())
            elif isinstance(entry, list):
                for idx, item in enumerate(entry):
                    if hasattr(item, 'to_bin'):
                        extend(item.to_bin())
                    else:
                        primitive_type = member_type_info.additional_info[
                            idx
                        ].value
                        ctype_primitive = PrimitiveTypeConversionSet[
                            primitive_type
                        ]
                        extend(pack(ctype_primitive, item))
            else:
                if issubclass(field_type, _Pointer):
                    count = getattr(self, 'count')
                    if issubclass(field_type._type_, Structure):
                        for item in entry[:count]:
                            extend(item.to_bin())
                    else:
                        extend(pack('%i%s' % (count, field_type._type_._type_),
                                    *entry[:count]))
                else:
                    extend(pack(field_type._type_, entry))
        return document


class BinaryRecordStructure(SimpleSerializerMixin, Structure):
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
