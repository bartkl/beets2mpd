use rusqlite::{Connection, Result};
use std::fs;
use std::io::{Seek, SeekFrom, Write};
//use std::time::Instant;

/* Config. */

const MUSIC_ROOT_DIR: &str = "/media/droppie/libraries/music";
const BEETS_DB_FILEPATH: &str = "./examples/library.db";
const TAGCACHE_FILEPATH: &str = "./tag_cache";
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
    composer_sort: String,
    arranger: String,
    mb_artistid: String,
    mb_albumartistid: String,
    mb_albumid: String,
    mb_trackid: String,
    mb_releasetrackid: String,
    label: String,
    work: String,
    grouping: String,
    mb_workid: String,
    genres: Vec<String>,
}

//genres: Vec<String>,

fn main() -> Result<()> {
    let mut output = fs::OpenOptions::new()
        .write(true)
        .append(true)
        .open(&TAGCACHE_FILEPATH)
        .unwrap();

    output.set_len(0);  // Truncate file.
    output.write(format!(
"info_begin
format: {}
mpd_version: {}
fs_charset: {}
tag: Artist
tag: ArtistSort
tag: Album
tag: AlbumSort
tag: AlbumArtist
tag: AlbumArtistSort
tag: Title
tag: TitleSort
tag: Track
tag: Genre
tag: Date
tag: OriginalDate
tag: Composer
tag: ComposerSort
tag: Performer
tag: Conductor
tag: Work
tag: Movement
tag: MovementNumber
tag: Ensemble
tag: Location
tag: Grouping
tag: Disc
tag: Label
tag: MUSICBRAINZ_ARTISTID
tag: MUSICBRAINZ_ALBUMID
tag: MUSICBRAINZ_ALBUMARTISTID
tag: MUSICBRAINZ_TRACKID
tag: MUSICBRAINZ_RELEASETRACKID
tag: MUSICBRAINZ_WORKID
info_end
", MPD_DB_FORMAT, MPD_VERSION, "UTF-8").as_bytes());


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
            items.composer_sort,
            items.arranger,
            items.mb_artistid,
            albums.mb_albumartistid,
            albums.mb_albumid,
            items.mb_trackid,
            items.mb_releasetrackid,
            albums.label,
            items.work,
            items.grouping,
            items.mb_workid,
            items.mb_releasetrackid
        from items
        left join albums
        on items.album_id = albums.id
        order by items.path, items.track
    ")?;
    let mut rows = albums_stmt.query_map([], |row| {
        Ok (DbItem {
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
            composer_sort: row.get(16)?,
            arranger: row.get(17)?,
            mb_artistid: row.get(18)?,
            mb_albumartistid: row.get(19)?,
            mb_albumid: row.get(20)?,
            mb_trackid: row.get(21)?,
            mb_releasetrackid: row.get(22)?,
            label: row.get(23)?,
            work: row.get(24)?,
            grouping: row.get(25)?,
            mb_workid: row.get(25)?,
            genres: row.get::<usize, String>(11)?.split(", ").map(|s| s.to_owned()).collect(),
        })
    })?;
    for item in rows {
        let song = item.unwrap();

        //let x = format!("Kankerhoer: {} asd {}", "A", "B");
        //output.write(x.as_bytes());
        output.seek(SeekFrom::End(0)).unwrap();
        output.write(format!(
"song_begin: {}
Time: {:.6}
Album: {}
AlbumArtist: {}
AlbumArtistSort: {}
Artist: {}
ArtistSort: {}
Title: {}
Label: {}
Track: {}
",
            song.album,
            1.000,
            song.album,
            song.albumartist,
            song.albumartist_sort,
            song.artist,
            song.artist_sort,
            song.title,
            song.label,
            song.track).as_bytes()).unwrap();
        for genre_value in song.genres {
            //output.seek(SeekFrom::End(0)).unwrap();
            output.write(format!("Genre: {}", genre_value).as_bytes());
        }
        output.write(format!("
Date: {}
OriginalDate: {}
Disc: {}
Composer: {}
ComposerSort: {}
Work: {}
Grouping: {}
MUSICBRAINZ_ARTISTID: {}
MUSICBRAINZ_ALBUMID: {}
MUSICBRAINZ_ALBUMARTISTID: {}
MUSICBRAINZ_TRACKID: {}
MUSICBRAINZ_RELEASETRACKID: {}
MUSICBRAINZ_WORKID: {}
mtime: {}
song_end",
            song.year,
            song.original_year,
            song.disc,
            song.composer,
            song.composer_sort,
            song.work,
            song.grouping,
            song.mb_artistid,
            song.mb_albumid,
            song.mb_albumartistid,
            song.mb_trackid,
            song.mb_releasetrackid,
            song.mb_workid,
            song.item_added).as_bytes());
    }

    Ok(())
}
