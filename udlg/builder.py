# -*- coding: utf-8 -*-
"""
.. module:: udlg.builder
    :synopsis: Builder
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from . import structure
from .enums import RecordTypeEnum
from .structure import Record, UDLGFile


class BinaryFormatterFileBuilder(object):
    @classmethod
    def build(cls, stream):
        """
        build .net binary data structure record from serialized stream

        :param stream: stream object
        :rtype: structure.
        :return:
        :raises EnvironmentError:
            - if stream was opened not in binary mode
        """
        if 'b' not in stream.mode:
            stream.close()
            raise EnvironmentError(
                "You should open stream with `binary` (b) flag"
            )
        document = structure.BinaryDataStructureFile()
        document.header._initiate(stream)
        records = list()
        append = records.append

        #: id: info
        object_id_map = {}
        reference_map = {}
        count = 0
        while True:
            record = Record()
            record._object_id_map = object_id_map
            record._reference_map = reference_map
            record._initiate(stream=stream, object_id_map=object_id_map,
                             reference_map=reference_map)
            append(record)
            count += 1
            if record.record_type == RecordTypeEnum.MessageEnd:
                break
        document.records = (Record * len(records))(*records)
        document.count = count
        return document


class UDLGBuilder(BinaryFormatterFileBuilder):
    @classmethod
    def build(cls, stream):
        document = UDLGFile()
        document._initiate(stream)
        document.data = super(UDLGBuilder, cls).build(stream)
        return document
