#!/usr/bin/env python3

import sqlite3
import os
import sys
import time


### Config.

# Paths.
MUSIC_ROOT_DIR = '/media/droppie/libraries/music'
BEETS_DB_FILEPATH = '/media/droppie/libraries/music/.meta/beets/library.db'
TAGCACHE_FILEPATH = '/media/droppie/libraries/music/.meta/mpd/tag_cache'

# MPD.
MPD_DB_FORMAT = 2
MPD_VERSION = '0.21.19'

# Delimiter used for multi-valued genres in Beets's `genre` field.
GENRE_DELIMITER = ', '


### Main.

if __name__ == '__main__':
    script_start_time = time.time()

    fs_charset = sys.getfilesystemencoding().upper()
    print(f"Using filesystem character set: {fs_charset}.")

    # Determine path format.
    if MUSIC_ROOT_DIR[0] == '/':
        print("Library seems to use POSIX paths.")
        import posixpath as ospath
    else:
        print("Library seems to use Windows paths.")
        import ntpath as ospath

    # Database connection.
    print("Connecting to Beets database...", end='')
    beets_conn = sqlite3.connect(BEETS_DB_FILEPATH)
    print(" OK.")
    beets_cursor = beets_conn.cursor()

    # Tagcache file initialisation.
    tagcache = open(TAGCACHE_FILEPATH, 'w')

    # Query the Beets database for all items.
    print("Preparing query on Beets database...", end='')
    beets_cursor.execute('''
        select
            items.path,
            items.length,
            items.artist,
            items.artist_sort,
            items.album,
            albums.albumartist,
            albums.albumartist_sort,
            items.title,
            items.track,
            albums.genre,
            albums.year,
            albums.original_year,
            items.disc,
            items.composer,
            items.arranger,
            items.mb_artistid,
            albums.mb_albumartistid,
            albums.mb_albumid,
            items.mb_trackid,
            items.mb_releasetrackid,
            albums.label
        from items

        left join albums
        on items.album_id = albums.id

        order by items.path, items.track
    ''')
    print(" OK.")

    print("Writing MPD tag cache file...", end='')
    # Write tag_cache header.
    tagcache.write(f'''\
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

    # This list keeps track of what directory we're in.
    # Based on this, I can close and open directory blocks during iteration.
    path_cursor = []
    for (path,
         length,
         artist,
         artist_sort,
         album,
         albumartist,
         albumartist_sort,
         title,
         track,
         genre,
         year,
         original_year,
         disc,
         composer,
         arranger,
         mb_artistid,
         mb_albumartistid,
         mb_albumid,
         mb_trackid,
         mb_releaseid,
         label) in beets_cursor:

        # Parse the `genre` value which could be multi-valued.
        if genre:
            genres = genre.split(GENRE_DELIMITER)
        else:
            genres = ''

        if isinstance(path, bytes):
            path = path.decode(fs_charset)

        mtime_item = os.path.getmtime(path)
        mtime_album = os.path.getmtime(os.path.dirname(path))

        # Get album dir relative to `MUSIC_ROOT_DIR`.
        album_dir = ospath.dirname(path[len(MUSIC_ROOT_DIR):]).lstrip(ospath.sep)
        album_dir_parts = album_dir.split(ospath.sep)

        # Check if we're still working on the same directory, and if not: handle that.
        if path_cursor != album_dir_parts:
            # If this is the first entry, `path_cursor` is empty so there's nothing to close.
            if path_cursor:

                # Album changed, close the necessary directories.
                first_diff_idx = [t[0] == t[1]  # Determine the index from which the path
                                                # cursor and current album path are different.
                                                # This allows you to close the difference on
                                                # `path_cursor`, and open directory blocks for
                                                # the difference in `album_dir_parts`.
                    for t in zip(album_dir_parts, path_cursor)].index(False)

                # Close dir blocks that are done.
                from_end_to_first_diff = slice(-1, first_diff_idx-len(path_cursor)-1, -1)
                for i, _ in enumerate(path_cursor[from_end_to_first_diff]):
                    from_start_to_i = slice(0, len(path_cursor) - i)
                    tagcache.write(f'''\
end: {os.sep.join(path_cursor[from_start_to_i])}
''')

            # Album changed, so open the necessary new blocks.
            start_idx = first_diff_idx if path_cursor else 0
            for i, path_part in enumerate(album_dir_parts[start_idx:]):
                from_first_diff_to_i = slice(0, start_idx + i + 1)
                tagcache.write(f'''\
directory: {path_part}
mtime: {mtime_album}
begin: {os.sep.join(album_dir_parts[from_first_diff_to_i])}
''')
            path_cursor = album_dir_parts

        # Write song block.
        tagcache.write(f'''\
song_begin: {path.split(ospath.sep)[-1]}
Time: {length:.6f}
Album: {album}
AlbumArtist: {albumartist}
AlbumArtistSort: {albumartist_sort}
Artist: {artist}
ArtistSort: {artist_sort}
Title: {title}
Label: {label}
Track: {track}
''')
        for genre_value in genres:
            tagcache.write(f'Genre: {genre_value}' + os.linesep)
        tagcache.write(f'''\
Date: {year}
OriginalDate: {original_year}
Disc: {disc}
Composer: {composer}
MUSICBRAINZ_ARTISTID: {mb_artistid}
MUSICBRAINZ_ALBUMID: {mb_albumid}
MUSICBRAINZ_ALBUMARTISTID: {mb_albumartistid}
MUSICBRAINZ_TRACKID: {mb_trackid}
MUSICBRAINZ_RELEASETRACKID: {mb_releaseid}
mtime: {mtime_item}
song_end
''')

    # Close final directories.
    for i, _ in enumerate(path_cursor[::-1]):
        from_start_to_i = slice(0, len(path_cursor) - i)
        tagcache.write(f'''\
end: {os.sep.join(path_cursor[from_start_to_i])}
''')
    # print('.', end='')
    print(" OK.")

    print("Cleaning up...", end='')
    # Cleanup.
    beets_cursor.close()
    beets_conn.close()
    tagcache.close()
    print(" OK.")

    print()
    print(f'Finished OK. ({time.time() - script_start_time:.3f} secs)')
