# -*- coding: utf-8 -*-
"""
.. module:: udlg.utils.bin
    :synopsis: Binary utils
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from functools import partial


def search(sequence, stream, stream_offset=0x0):
    """
    process simple search sequence inside stream

    :param stream: stream object, file
    :param bytes | str sequence: binary sequence to find
    :param int stream_offset: stream offset where process should start from,
        0x0 by default
    :rtype: int
    :return: index or offset found sequence
    :raise IndexError:
        - if nothing was found
    """
    if isinstance(sequence, str):
        sequence = bytes(sequence.encode('utf-8'))
    elif isinstance(sequence, bytes):
        pass
    else:
        raise TypeError("`sequence` should be str, bytes "
                        "instance")

    chunk_size = 1
    pos = stream.tell()
    offset = 0
    stream.seek(stream_offset)
    # byte = stream.read(1)
    stream_by_byte = partial(stream.read, chunk_size)
    to_int = partial(int.from_bytes, byteorder='little')
    sequence_length = len(sequence)
    found = -1
    for sign in iter(stream_by_byte, b''):
        byte = to_int(sign)
        if offset == sequence_length:
            found = stream.tell() - (len(sequence) + 1)
            break
        if offset < sequence_length and byte == sequence[offset]:
            offset += 1
        elif offset and byte != sequence[offset]:
            offset = 0
        else:
            pass
    else:
        raise IndexError("sequence `%r` not found" % sequence)
    stream.seek(pos)
    return found


def search_all(sequence, stream):
    """
    search all sequence pattern inside stream

    :param stream: stream object, file
    :param bytes | str sequence: sequence to found
    :rtype: list
    :return: list of found position inside stream for given sequence
    """
    if isinstance(sequence, str):
        sequence = bytes(sequence.encode('utf-8'))
    elif isinstance(sequence, bytes):
        pass
    else:
        raise TypeError('sequences should be str or bytes instance')

    last_offset = 0x0
    indexes = []
    sequence_length = len(sequence)
    while 1:
        try:
            last_offset = search(
                sequence, stream, stream_offset=last_offset + sequence_length
            )
            indexes.append(last_offset)
        except IndexError:
            break
    return indexes
