#!/usr/bin/env python3
import io
import os
import subprocess
import sys
import time

from pathlib import Path
from typing import TextIO


starttime = time.time()


def _exit(retcode: int, msg: str = ''):
    if msg:
        print(msg)
    sys.exit(retcode)
    

FIELDS = {
    'header': {
        'directory_info_begin': 'info_begin',
        'directory_info_end': 'info_end',
        'db_format_prefix': 'format: ',
        'directory_mpd_version': 'mpd_version: ',
        'directory_fs_charset': 'fs_charset: ',
        'db_tag_prefix': 'tag: ',
        'db_format': 2
    },
    'directory': {
        'directory_dir': 'directory: ',
        'directory_type': 'type: ',
        'directory_mtime': 'mtime: ',
        'directory_begin': 'begin: ',
        'directory_end': 'end: '

    },
    'song': {
        'song_mtime': 'mtime',
        'song_en': 'song_end'
    }
}


def get_mpd_version() -> str:
    result = subprocess.run('mpd --version | head -1', shell=True,
                             capture_output=True).stdout.decode('utf8')
    version = result.split(' ')[-1][1:-2]
    return version
        

def write_tagcache(buffer: TextIO, music_root: Path):
    """Writes the MPD tag cache file to the provided text buffer."""

    fs_charset = sys.getfilesystemencoding().upper()
    # mpd_version = get_mpd_version()
    mpd_version = "aa"

    header = FIELDS['header']
    buffer.write('\n'.join([
        f'{header["directory_info_begin"]}',
        f'{header["db_format_prefix"]}{header["db_format"]}',
        f'{header["directory_mpd_version"]}{mpd_version}',
        f'{header["directory_fs_charset"]}{fs_charset}']))


if __name__ == '__main__':
    with open('test_tagcache', 'w') as f:
        write_tagcache(f, Path())


    endtime = time.time()
    print("It took {:.8f} seconds.".format(endtime-starttime))
