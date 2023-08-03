use rusqlite::{Connection, Result};
use std::fs::File;
use std::io::Write;
use std::time::Instant;

/* Config. */

const MUSIC_ROOT_DIR: &str = "/media/droppie/libraries/music";
const BEETS_DB_FILEPATH: &str = "library.db";
const TAGCACHE_FILEPATH: &str = "tag_cache";
const MPD_DB_FORMAT: u8 = 2;
const MPD_VERSION: &str = "0.24";
const GENRE_DELIMITER: &str = ", ";

/* Types. */

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

//#[derive(Debug)]
//struct Track {
//    db_item: DbItem,
//    genres: Vec<String>,
//    mtime_item: Option<u32>,
//    mtime_album: Option<u32>,
//}

fn main() -> Result<()> {
    let conn = Connection::open(&BEETS_DB_FILEPATH)?;

    let mut albums_stmt = conn.prepare(
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
    ",)?;

    let mut names = Vec::new();
    let mut rows = albums_stmt.query([])?;
    while let Some(row) = rows.next()? {
        names.push(row.get(0)?);
    }
    println!("{}", names.len());
    //println!("{:?}", names);
    Ok(())
}
