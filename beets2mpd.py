#!/usr/bin/env python3

import sqlite3
import os
import time

if __name__ == '__main__':
    starttime = time.time()

    LIB_ROOTPATH =  'E:\\Music-Beets'
    BEETS_DB_FILEPATH = '/home/bart/music_library.db'
    TAGCACHE_FILEPATH = '/home/bart/tagcache_test'
    GENRE_DELIMITER = ','


    if LIB_ROOTPATH[0] == "/":
        import posixpath as ospath
    else:
        import ntpath as ospath


    # Database connection
    db_connection = sqlite3.connect(BEETS_DB_FILEPATH, detect_types=sqlite3.PARSE_COLNAMES)
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
            path = path.decode('utf8')
        album_directory = ospath.dirname(path[len(LIB_ROOTPATH):]).lstrip(ospath.sep)

        # `genre` can be comma separated multi-valued, so rename it to `genres`
        # for clarity while parsing.
        if genre:
            genres = genre.split(GENRE_DELIMITER)
        else:
            genres = ''

        # If album changed, close the previous block
        if album_directory != last_processed_album_directory and last_processed_album_directory is not None:
                tagcache_filehandle.write("end: %s\n" % last_processed_album_directory) # previous directory :)

        # If album changed, open new block
        if album_directory != last_processed_album_directory:
            tagcache_filehandle.write("directory: %s\n" % album_directory) 
            tagcache_filehandle.write("mtime: 0\n") 
            tagcache_filehandle.write("begin: %s\n" % album_directory)
            last_processed_album_directory = album_directory

        # Write song block
        tagcache_filehandle.write("song_begin: %s\n" % path.split(ospath.sep)[-1])
        tagcache_filehandle.write("Time: %.6f\n" % length)
        tagcache_filehandle.write("Artist: %s\n" % artist)
        tagcache_filehandle.write("Album: %s\n" % album)
        tagcache_filehandle.write("AlbumArtist: %s\n" % albumartist)
        tagcache_filehandle.write("Title: %s\n" % title)
        tagcache_filehandle.write("Track: %s\n" % track)
        for genre_ in genres:
                tagcache_filehandle.write("Genre: %s\n" % genre_)
        tagcache_filehandle.write("Date: %s\n" % year)
        tagcache_filehandle.write("Disc: %s\n" % disc)
        tagcache_filehandle.write("Composer: %s\n" % composer)
        tagcache_filehandle.write("Performer: %s\n" % arranger) # Not sure about this one
        tagcache_filehandle.write("mtime: 0\n") 
        tagcache_filehandle.write("song_end\n")

    # Cleanup
    cursor.close()
    db_connection.close()
    tagcache_filehandle.close()

    endtime = time.time()
    print("It took {:.8f} seconds.".format(endtime-starttime))
