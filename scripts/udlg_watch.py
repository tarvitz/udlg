#!/usr/bin/env python3.4
import os
import sys
import json
import struct
from collections import defaultdict
from contextlib import closing
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, BASE_DIR)

from udlg.builder import UDLGBuilder

BASE_DIR = os.path.abspath(os.getcwd())
DIALOGS_DIR = os.path.join(
    os.path.join(
        BASE_DIR, 'remote/Data/Dialogs'
    )
)
BEFORE_START_HEADER_OFFSET = 0x34

SIZES = {
    1: 'B',  #: unsigned byte
    2: 'H',  #: unsigned short
    4: 'I',  #: unsigned int32
    8: 'Q'   #: unsigned int64
}


def process(entries, opts, storage=None):
    storage = storage if storage is not None else defaultdict(list)
    #: process options
    size = opts.size or 0x8
    offset = int(opts.offset, 0x0)

    for entry in entries:
        with closing(open(entry, 'rb')) as udlg_file:
            udlg = UDLGBuilder.build(stream=udlg_file)
            udlg_file.seek(offset)
            udlg_file.seek(len(udlg.header) + BEFORE_START_HEADER_OFFSET, 1)
            fmt = SIZES[size]
            data, = struct.unpack(fmt, udlg_file.read(size))
            storage[data].append(entry)
            entry_name = entry.rsplit('/', 1)[-1]
            print("Processing %s, found: %s" % (entry_name, data))


def main(opts):
    storage = defaultdict(list)
    entries = json.loads(open('dialogs.json', 'r').read())
    process(entries, opts, storage=storage)
    open(opts.output, 'w').write(json.dumps(storage))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--offset', dest='offset', help='set offset',
                        default='0x0')
    parser.add_argument('--size', dest='size', help='size, 1, 2, 4, 8',
                        type=int)
    parser.add_argument('-o', '--output', dest='output',
                        default='output.json', help='output file to write')
    arguments = parser.parse_args()
    main(arguments)
