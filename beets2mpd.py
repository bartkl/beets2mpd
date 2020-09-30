#!/usr/bin/env python3

import sqlite3
import os
import time


MUSIC_ROOT_DIR =  'E:\\Music-Beets'  # Must be an absolute path.
BEETS_DB_FILEPATH = '/home/bart/music_library.db'
TAGCACHE_FILEPATH = '/home/bart/tagcache_test'
GENRE_DELIMITER = ','
MPD_VERSION = '0.21.19'


if __name__ == '__main__':
    starttime = time.time()

    if MUSIC_ROOT_DIR[0] == '/':
        import posixpath as ospath
    else:
        import ntpath as ospath

    # Database connection
    db_connection = sqlite3.connect(BEETS_DB_FILEPATH)
    cursor = db_connection.cursor()

    # Tagcache file initialisation
    tagcache_filehandle = open(TAGCACHE_FILEPATH, 'w')

    # Fetch items from beets database
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

    # Write tag_cache
    tagcache_filehandle.writelines('''\
    info_begin
    format: 2
    mpd_version: 0.19.1
    fs_charset: UTF-8
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
    tag: Composer
    tag: Performer
    tag: Disc
    tag: MUSICBRAINZ_ARTISTID
    tag: MUSICBRAINZ_ALBUMID
    tag: MUSICBRAINZ_ALBUMARTISTID
    tag: MUSICBRAINZ_TRACKID
    tag: MUSICBRAINZ_RELEASETRACKID
    info_end
    ''')

    last_processed_album_directory = None
    for (\
        path,\
        length,\
        artist,\
        album,\
        albumartist,\
        title,\
        track,\
        genre,\
        year,\
        disc,\
        composer,\
        arranger\
    ) in cursor:
        if isinstance(path, bytes):
            path = path.decode('utf-8')
        album_directory = ospath.dirname(path[len(MUSIC_ROOT_DIR):]).lstrip(ospath.sep)

        # `genre` can be comma separated multi-valued, so rename it to `genres`
        # for clarity while parsing.
        if genre:
            genres = genre.split(GENRE_DELIMITER)
        else:
            genres = ''

        # If album changed, close the previous block
        if album_directory != last_processed_album_directory and last_processed_album_directory is not None:
            tagcache_filehandle.write(f'end: {last_processed_album_directory}' + os.linesep) # previous directory :)

        # If album changed, open new block
        if album_directory != last_processed_album_directory:
            tagcache_filehandle.write(os.linesep.join((
                f'directory: {album_directory}',
                f'mtime: 0',  # Currently hard-coded at 0.
                f'begin: {album_directory}')))
            last_processed_album_directory = album_directory

        # Write song block
        tagcache_filehandle.write(os.linesep.join((
            f'song_begin: {path.split(ospath.sep)[-1]}'
            f'Time: {length:.6f}',
            f'Artist: {artist}',
            f'Album: {album}',
            f'AlbumArtist: {albumartist}',
            f'Title: {title}',
            f'Track: {track}')))
        for genre_value in genres:
            tagcache_filehandle.write(f'Genre: {genre_value}' + os.linesep)
        tagcache_filehandle.write(os.linesep.join((
            f'Date: {year}',
            f'Disc: {disc}',
            f'Composer: {composer}',
            f'Performer: {arranger}',  # Not sure about this one
            f'mtime: 0'  # Currently hard-coded at 0.
            f'song_end')))

    # Cleanup
    cursor.close()
    db_connection.close()
    tagcache_filehandle.close()

    endtime = time.time()
    print('It took {:.3f} seconds.'.format(endtime-starttime))
