#!/usr/bin/env python3

import sqlite3
import os
import sys
import time


MUSIC_ROOT_DIR = '/media/droppie/libraries/music'
BEETS_DB_FILEPATH = '/media/droppie/libraries/music/.config/beets/library.db'
MPD_DB_FORMAT = 2
TAGCACHE_FILEPATH = '/home/bart/tagcache_test'
GENRE_DELIMITER = ', '
MPD_VERSION = '0.21.19'


if __name__ == '__main__':
    starttime = time.time()

    fs_charset = sys.getfilesystemencoding().upper()

    # Windows paths or UNIX paths.
    if MUSIC_ROOT_DIR[0] == '/':
        import posixpath as ospath
    else:
        import ntpath as ospath

    # Database connection.
    db_connection = sqlite3.connect(BEETS_DB_FILEPATH)
    cursor = db_connection.cursor()

    # Tagcache file initialisation.
    tagcache_filehandle = open(TAGCACHE_FILEPATH, 'w')

    # Query the Beets database for all items.
    cursor.execute('''
        select
            items.path,
            items.length,
            items.artist,
            items.album,
            albums.albumartist,
            items.title,
            items.track,
            albums.genre,
            albums.year,
            items.disc,
            items.composer,
            items.arranger
        from items

        left join albums
        on items.album_id = albums.id

        order by items.path, items.track
    ''')

    # Write tag_cache header.
    tagcache_filehandle.write(f'''\
info_begin
format: {MPD_DB_FORMAT}
mpd_version: {MPD_VERSION}
fs_charset: {fs_charset}
tag: Artist
tag: ArtistSort
tag: Album
tag: AlbumSort
tag: AlbumArtist
tag: AlbumArtistSort
tag: Title
tag: Track
tag: Name
tag: Genre
tag: Date
tag: OriginalDate
tag: Composer
tag: Performer
tag: Disc
tag: Label
tag: MUSICBRAINZ_ARTISTID
tag: MUSICBRAINZ_ALBUMID
tag: MUSICBRAINZ_ALBUMARTISTID
tag: MUSICBRAINZ_TRACKID
tag: MUSICBRAINZ_RELEASETRACKID
tag: MUSICBRAINZ_WORKID
info_end
''')

    last_processed_album_directory = None
    for (path,
         length,
         artist,
         album,
         albumartist,
         title,
         track,
         genre,
         year,
         disc,
         composer,
         arranger) in cursor:
        if isinstance(path, bytes):
            path = path.decode('utf-8')
        album_directory = ospath.dirname(path[len(MUSIC_ROOT_DIR):]).lstrip(ospath.sep)

        # `genre` can be multi-valued, so rename it to `genres` for clarity while parsing.
        if genre:
            genres = genre.split(GENRE_DELIMITER)
        else:
            genres = ''

        # If album changed, close the previous block.
        if album_directory != last_processed_album_directory and last_processed_album_directory is not None:
            # Previous directory:
            tagcache_filehandle.write(f'''\
end: {last_processed_album_directory}
''')

        # If album changed, open new block.
        if album_directory != last_processed_album_directory:
            tagcache_filehandle.write(f'''\
directory: {album_directory}
mtime: 0
begin: {album_directory}
''')
            last_processed_album_directory = album_directory

        # Write song block.
        tagcache_filehandle.write(f'''\
song_begin: {path.split(ospath.sep)[-1]}
Time: {length:.6f}
Artist: {artist}
Album: {album}
AlbumArtist: {albumartist}
Title: {title}
Track: {track}
''')
        for genre_value in genres:
            tagcache_filehandle.write(f'Genre: {genre_value}' + os.linesep)
        tagcache_filehandle.write(f'''\
Date: {year}
Disc: {disc}
Composer: {composer}
Performer: {arranger}
mtime: 0
song_end
''')

    # Cleanup.
    cursor.close()
    db_connection.close()
    tagcache_filehandle.close()

    endtime = time.time()
    print('It took {:.3f} seconds.'.format(endtime-starttime))
