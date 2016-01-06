#!/usr/bin/env python3.5
import sys
import os
import argparse
from contextlib import closing

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

sys.path.insert(0, ROOT_DIR)
from udlg.builder import UDLGBuilder

import logging
logger = logging.getLogger(__file__)


def unpack(entry, opts):
    with closing(open(entry.path, 'rb')) as stream:
        store_path = os.path.join(
            opts.output_dir, entry.path.split(opts.dialogs_dir)[-1][1:]
        ).replace('\\', '/')
        i18n_path = os.path.join(
            opts.i18n_dir, entry.path.split(opts.dialogs_dir)[-1][1:]
        ).replace('\\', '/').replace('.udlg', '.txt')
        store_entry_path, store_entry = store_path.rsplit('/', 1)
        if not os.path.exists(store_entry_path):
            os.makedirs(store_entry_path)

        if not(opts.skip_processed and os.path.exists(store_path)):
            print("Processing: %s" % entry.path)
            try:
                i18n_block = open(i18n_path, 'rb').read()
            except OSError:
                logger.error("Can not access i18n file: %s, skipping",
                             i18n_path)
                return
            u = UDLGBuilder.build(stream)
            u.load_i18n(i18n_block)
            open(store_path, 'wb').write(u.to_bin())

        else:
            print("Skipping: %s" % entry.path)


def process(opts, path=None):
    path = path or opts.dialogs_dir
    for entry in os.scandir(path):
        if entry.is_dir():
            process(opts, path=entry.path)
        else:
            if not entry.name.endswith('.udlg'):
                continue
            unpack(entry, opts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dialogs', dest='dialogs_dir',
                        required=True, metavar='Dialogs',
                        help='Underrail Data/Dialogs directory')
    parser.add_argument('-o', '--output', dest='output_dir',
                        metavar='dir', help='output directory', default='.',
                        required=False)
    parser.add_argument('-T', '--i18n-dir', dest='i18n_dir',
                        metavar='dir', help='i18n directory',
                        required=True)
    parser.add_argument('-S', '--skip-processed', dest='skip_processed',
                        help='do not process files already had been processed',
                        action='store_true', required=False, default=False)
    arguments = parser.parse_args()
    process(arguments)
