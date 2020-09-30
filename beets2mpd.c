#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <sqlite3.h>
#include <time.h>
#include <string.h>


const char* LIBROOT = "E:\\Music-Beets\\";
const char* TAG_CACHE_FILEPATH = "/home/bart/tag_cache";
const char* BEETS_DB_PATH = "/home/bart/music_library.db";

const char* GET_ALL_SONGS_SQL =
    "SELECT\n"
    "    items.path,\n"
    "    items.length,\n"
    "    items.artist,\n"
    "    items.album,\n"
    "    albums.albumartist,\n"
    "    items.title,\n"
    "    items.track,\n"
    "    albums.genre,\n"
    "    albums.year,\n"
    "    items.disc,\n"
    "    items.composer,\n"
    "    items.arranger\n"
    "FROM items\n"
    "\n"
    "LEFT JOIN albums\n"
    "ON items.album_id = albums.id\n"
    "\n"
    "ORDER BY items.path, items.track\n";

int main(void) {
    clock_t start;
    double cpu_time_elapsed;
    start = clock();

    sqlite3 *db;
    sqlite3_stmt *result;


    int cursor = sqlite3_open(BEETS_DB_PATH, &db);
    
    if (cursor != SQLITE_OK) {
        fprintf(stderr, "Cannot open database: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        
        return 1;
    }
    
    cursor = sqlite3_prepare_v2(db, GET_ALL_SONGS_SQL, -1, &result, 0);    
    
    if (cursor != SQLITE_OK) {
        fprintf(stderr, "Failed to fetch data: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        
        return 1;
    }    

    FILE *tagCacheFile = fopen(TAG_CACHE_FILEPATH, "w");
    while (true) {
        cursor = sqlite3_step(result);

        const char *path = sqlite3_column_text(result, 0);
        const char *length = sqlite3_column_text(result, 1);
        const char *artist = sqlite3_column_text(result, 2);
        const char *album = sqlite3_column_text(result, 3);
        const char *albumartist = sqlite3_column_text(result, 4);
        const char *title = sqlite3_column_text(result, 5);
        const char *track = sqlite3_column_text(result, 6);
        const char *genre = sqlite3_column_text(result, 7);
        const char *year = sqlite3_column_text(result, 8);
        const char *disc = sqlite3_column_text(result, 9);
        const char *composer = sqlite3_column_text(result, 10);
        const char *arranger = sqlite3_column_text(result, 11);

        char* albumpath[strlen(path)];
        strcpy(path, albumpath);
        printf(albumpath);
        while (albumpath=strstr(albumpath,LIBROOT))
            memmove(albumpath,albumpath+strlen(LIBROOT),1+strlen(albumpath+strlen(LIBROOT)));

        return 0;

        

        if (cursor == SQLITE_ROW) {
            fprintf(tagCacheFile ,"%s\n", sqlite3_column_text(result, 0));
            fprintf(tagCacheFile ,"%s\n", sqlite3_column_text(result, 1));
            fprintf(tagCacheFile ,"%s\n", sqlite3_column_text(result, 2));
            fprintf(tagCacheFile ,"%s\n", sqlite3_column_text(result, 3));
            fprintf(tagCacheFile ,"%s\n", sqlite3_column_text(result, 4));
            fprintf(tagCacheFile ,"%s\n", sqlite3_column_text(result, 5));
            fprintf(tagCacheFile ,"%s\n", sqlite3_column_text(result, 6));
            fprintf(tagCacheFile ,"%s\n", sqlite3_column_text(result, 7));
            fprintf(tagCacheFile ,"%s\n", sqlite3_column_text(result, 8));
            fprintf(tagCacheFile ,"%s\n", sqlite3_column_text(result, 9));
            fprintf(tagCacheFile ,"%s\n", sqlite3_column_text(result, 10));
            fprintf(tagCacheFile ,"%s\n", sqlite3_column_text(result, 11));
        }
        else {
            break;
        }
    }
    
    sqlite3_finalize(result);
    sqlite3_close(db);

    cpu_time_elapsed = clock() - start;

    int msec = cpu_time_elapsed * 1000 / CLOCKS_PER_SEC;
    printf("Time taken %d seconds %d milliseconds", msec/1000, msec%1000);
    
    return 0;
}
