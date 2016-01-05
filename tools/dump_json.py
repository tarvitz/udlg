#!/usr/bin/env python3.5
import json
import sys
import os
import argparse
from contextlib import closing

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

sys.path.insert(0, ROOT_DIR)
from udlg.builder import UDLGBuilder


def unpack(entry, opts):
    with closing(open(entry.path, 'rb')) as stream:
        store_path = os.path.join(
            opts.output_dir, entry.path.split(opts.dialogs_dir)[-1][1:]
        )
        i18n_path, file_name = store_path.rsplit('/', 1)
        if not os.path.exists(i18n_path):
            os.makedirs(i18n_path)
        file_name = file_name.replace('.udlg', '.json')
        store_path = os.path.join(i18n_path, file_name)
        if not(opts.skip_processed and os.path.exists(store_path)):
            print("Processing: %s" % entry.path)
            u = UDLGBuilder.build(stream)
            open(store_path, 'w').write(json.dumps(u.to_dict()))
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
    parser.add_argument('-S', '--skip-processed', dest='skip_processed',
                        help='do not process files already had been processed',
                        action='store_true', required=False, default=False)
    arguments = parser.parse_args()
    process(arguments)
