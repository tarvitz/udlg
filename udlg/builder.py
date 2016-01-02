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
from .structure import Record


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
        while True:
            record = Record()
            #: todo make _initiate more generic
            record._initiate(stream=stream)
            append(record)
            if record.record_type == RecordTypeEnum.MessageEnd:
                break
        document.records = (Record * len(records))(*records)
        return document


class UDLGBuilder(object):
    def __init__(self, filename=''):
        """

        :param str filename: filename to open
        :param stream:
        :return:
        """
        self.stream = open(filename, 'rb')

    def __del__(self):
        self.stream.close()
        super(UDLGBuilder, self).__del__()

    @classmethod
    def build(cls, stream):
        document = structure.UDLG()
        document.start._initiate(stream)
        document.header._initiate(stream)
        return document


