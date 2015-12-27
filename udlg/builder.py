# -*- coding: utf-8 -*-
"""
.. module:: udlg.builder
    :synopsis: Builder
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from . import structure


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
