#!/usr/bin/env python3.4
import os
import sys
sys.path.insert(0, os.path.dirname('.'))

import argparse
from contextlib import closing
from udlg.builder import UDLGBuilder
from udlg.structure.records import MessageEnd


def process(source, opts):
    with closing(open(source, 'rb')) as udlg_file:
        return UDLGBuilder.build(stream=udlg_file)


def main(opts):
    source = opts.source
    return process(source, opts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', dest='source',
                        metavar='file.udlg',
                        help='source file to inspect', required=True)
    arguments = parser.parse_args()
    udlg_file = main(arguments)
    record_list = udlg_file.data.records
    count = udlg_file.data.count
    last_block = record_list[count - 1].entry
    assert isinstance(last_block, MessageEnd),\
        "Check failed, wrong last record block type: `%r`" % type(last_block)
