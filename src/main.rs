use rusqlite::{Connection, Result};
use std::fs::File;
use std::io::Write;
use std::time::Instant;

//// Config.

// Paths.
const MUSIC_ROOT_DIR: &str = "/media/droppie/libraries/music";
const BEETS_DB_FILEPATH: &str = "library.db";
const TAGCACHE_FILEPATH: &str = "tag_cache";

// MPD.
const MPD_DB_FORMAT: u8 = 2;
const MPD_VERSION: &str = "0.21.19";

// Delimiter used for multi-valued genres in Beets's `genre` field.
const GENRE_DELIMITER: &str = ", ";

// Retrieve and write actual modified times for files and dirs.
// Note that this makes the script significantly slower.
const SET_MTIME: bool = true;

//// Types.

#[derive(Debug)]
struct DbItem {
    path: Vec<u8>,
    length: f32,
    artist: String,
    artist_sort: String,
    album: String,
    albumartist: String,
    albumartist_sort: String,
    title: String,
    track: u16,
    genre: String,
    year: u16,
    original_year: u16,
    disc: u8,
    composer: String,
    arranger: String,
    mb_artistid: String,
    mb_albumartistid: String,
    mb_albumid: String,
    mb_trackid: String,
    mb_releasetrackid: String,
    label: String,
}

#[derive(Debug)]
struct Track {
    db_item: DbItem,
    genres: Vec<String>,
    mtime_item: Option<u32>,
    mtime_album: Option<u32>,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let start = Instant::now();

    let fs_charset = "UTF-8";  // TODO: Get from env.
    println!("Using filesystem character set: {}.", fs_charset);

    // Determine path format.
    println!("Library seems to use POSIX paths.");  // TODO: Hardcoded for now.

    // Database connection.
    println!("Connecting to Beets database...");
    let conn = Connection::open(&BEETS_DB_FILEPATH)?;

    // Query the Beets database for all items.
    let mut stmt = conn.prepare(
        "
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
    ",
    )?;

    let items_iter = stmt.query_map([], |row| {
        let db_item = DbItem {
            path: row.get(0)?,
            length: row.get(1)?,
            artist: row.get(2)?,
            artist_sort: row.get(3)?,
            album: row.get(4)?,
            albumartist: row.get(5)?,
            albumartist_sort: row.get(6)?,
            title: row.get(7)?,
            track: row.get(8)?,
            genre: row.get(9)?,
            year: row.get(10)?,
            original_year: row.get(11)?,
            disc: row.get(12)?,
            composer: row.get(13)?,
            arranger: row.get(14)?,
            mb_artistid: row.get(15)?,
            mb_albumartistid: row.get(16)?,
            mb_albumid: row.get(17)?,
            mb_trackid: row.get(18)?,
            mb_releasetrackid: row.get(19)?,
            label: row.get(20)?,
        };

        let genres = db_item.genre.split(", ").map(|s| s.to_owned()).collect();
        Ok(Track {
            db_item,
            genres,
            mtime_item: Some(0),
            mtime_album: Some(0),
        })
    })?;
    
    // Tagcache file initialisation.
    let tag_cache_path = String::from("tagcache");  // TODO: Use tempfile.
    let mut tagcache = File::create(&tag_cache_path)?;

    // Write tag_cache header.
    let tagcache_header = format!(
"info_begin
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
info_end");
    tagcache.write(tagcache_header.as_bytes());

    // This list keeps track of what directory we're in.
    // Based on this, I can close and open directory blocks during iteration.
    let mut path_cursor = Vec<String>::new();

    for track in items_iter {
        writeln!(tagcache, "{}", track?.db_item.artist)?;
    }

    let duration = start.elapsed();
    println!("Took: {}", duration.as_secs_f32());
    Ok(())
}
