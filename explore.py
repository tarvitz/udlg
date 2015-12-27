#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
import os
import json


BASE_DIR = os.path.abspath(os.getcwd())
DIALOGS_DIR = os.path.join(
    os.path.join(
        BASE_DIR, 'remote/Data/Dialogs'
    )
)


def process(storage=None, path=None):
    storage = storage if storage is not None else []
    path = path or DIALOGS_DIR
    for entry in os.scandir(path):
        if entry.is_dir():
            process(storage, entry.path)
        else:
            if not entry.name.endswith('.udlg'):
                continue
            print("Processing: %s" % entry.name)
            storage.append(entry.path)


def main():
    files = []
    process(files)
    open('dialogs.json', 'w').write(json.dumps(files))


if __name__ == '__main__':
    main()
