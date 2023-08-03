use rusqlite::{Connection, Result};
use std::fs;
//use std::time::Instant;

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
    item_added: f32,
    album_added: f32,
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
}

fn main() -> Result<()> {
    let conn = Connection::open(&BEETS_DB_FILEPATH)?;

    //let mut stmt = conn.prepare("SELECT id, album FROM albums")?;
    let mut albums_stmt = conn.prepare(
        "
        select
            items.path,
            items.added as item_added,
            albums.added as album_added,
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
    ")?;
    let mut rows = albums_stmt.query_map([], |row| {
        let db_item = DbItem {
            path: row.get(0)?,
            item_added: row.get(1)?,
            album_added: row.get(2)?,
            length: row.get(3)?,
            artist: row.get(4)?,
            artist_sort: row.get(5)?,
            album: row.get(6)?,
            albumartist: row.get(7)?,
            albumartist_sort: row.get(8)?,
            title: row.get(9)?,
            track: row.get(10)?,
            genre: row.get(11)?,
            year: row.get(12)?,
            original_year: row.get(13)?,
            disc: row.get(14)?,
            composer: row.get(15)?,
            arranger: row.get(16)?,
            mb_artistid: row.get(17)?,
            mb_albumartistid: row.get(18)?,
            mb_albumid: row.get(19)?,
            mb_trackid: row.get(20)?,
            mb_releasetrackid: row.get(21)?,
            label: row.get(22)?,
        };

        let genres = db_item.genre.split(", ").map(|s| s.to_owned()).collect();
        Ok(Track {
            db_item,
            genres,
        })
    })?;
    for item in rows {
        println!("Album: {:?}", item.unwrap());
    }

    fs::write(&TAGCACHE_FILEPATH, "HERREUW").expect("Could not write.");


    //let mut rows = albums_stmt.query([])?;
    //let mut names = Vec::new();
    //while let Some(row) = rows.next()? {
    //    println!("A");
    //    //names.push(row.get(0)?);
    //}
    //println!("{}", names.len());
    //println!("{:?}", names);
    Ok(())
}
