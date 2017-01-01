#!/usr/bin/env python
#: will work on python 3.5+ only

import json
import sys
import os
import argparse
from contextlib import closing
from collections import defaultdict

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

sys.path.insert(0, ROOT_DIR)
from udlg import enums
from udlg.builder import UDLGBuilder

import logging
logger = logging.getLogger(__file__)

PROCESSING_MESSAGE_OK = 'file processing: %s - OK'
PROCESSING_MESSAGE_FAIL = 'file processing: %s - FAIL'
PROCESSING_MESSAGE_FOUND_IN_CACHE = 'file processing: %s - FOUND IN CACHE'


def inspect(entry, health, opts):
    with closing(open(entry.path, 'rb')) as stream:
        if opts.use_health_cache and entry.path in health:
            #: skip for caching
            logger.info(PROCESSING_MESSAGE_FOUND_IN_CACHE % entry.path)
            return

        try:
            doc = UDLGBuilder.build(stream)
            assert (
                doc.records[-1].record_type == enums.RecordTypeEnum.MessageEnd
            )
            logger.info(PROCESSING_MESSAGE_OK % entry.path)
            health[entry.path] = True
        except Exception as err:
            logger.info(PROCESSING_MESSAGE_FAIL % entry.path)
            health[entry.path] = False


def process(opts, path=None):
    path = path or opts.directory
    if opts.use_health_cache and os.path.exists(opts.output):
        health = json.loads(open(opts.output, 'r').read())
    else:
        health = defaultdict(list)
    recursive = opts.recursive

    for entry in os.scandir(path):
        if recursive and entry.is_dir():
            process(opts, path=entry.path)
        else:
            if not entry.name.endswith('.udlg'):
                continue
            inspect(entry, health, opts)
    open(opts.output, 'w').write(json.dumps(health))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', dest='directory',
                        required=True, metavar='directory',
                        help='directory where find udlg files')
    parser.add_argument('-o', '--output', dest='output',
                        metavar='dir', help='output file with health data',
                        default='health.json',
                        required=False)
    parser.add_argument('-r', '--recursive', dest='recursive',
                        action='store_true',
                        help='recursive')
    parser.add_argument('-c', '--health-cache', dest='use_health_cache',
                        action='store_true',
                        help='uses health cache (same file as output) to '
                             'prevent data from processing twice')
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true',
                        help='verbose output')
    arguments = parser.parse_args()
    if arguments.verbose:
        logging.basicConfig(level=logging.INFO)
    process(arguments)
