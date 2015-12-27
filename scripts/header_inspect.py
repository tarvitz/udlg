#!/usr/bin/env python3.4
import os
import sys
import json

from collections import OrderedDict
from contextlib import closing
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, BASE_DIR)
from udlg.builder import UDLGBuilder


def process(source, opts):
    with closing(open(source, 'rb')) as udlg_file:
        udlg = UDLGBuilder.build(stream=udlg_file)
        data = [(x.signature.decode('utf-8'), x.data) for x in udlg.header]
        hm = OrderedDict(data)
        return hm


def main(opts):
    source = opts.source
    return process(source, opts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', dest='source',
                        metavar='file.udlg',
                        help='source file to inspect', required=True)
    arguments = parser.parse_args()
    data = main(arguments)
    print(json.dumps(data, indent=4))
