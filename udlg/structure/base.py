# -*- coding: utf-8 -*-
"""
.. module:: udlg.structure.base
    :synopsis: Base classes for structures
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from ctypes import Structure, cast, pointer, c_void_p


class BinaryRecordStructure(Structure):
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
        raise NotImplementedError(
            "Initiate structure procedure was "
            "Not implemented for `%s` record class" % self.__class__.__name__
        )
