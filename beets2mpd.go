package main

import (
    "database/sql"
    "fmt"
    _ "github.com/mattn/go-sqlite3"
    "log"
)

func main() {
    fmt.Println("Hello, World!")
    db, err := sql.Open("sqlite3", "./library.db")

    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    stmt := `
        select id, album from albums
    `

    rows, err := db.Query(stmt)

    if err != nil {
        log.Fatal(err)
    }

    defer rows.Close()

    for rows.Next() {
        var id int
	var album string
	err = rows.Scan(&id, &album)
	if err != nil {
            log.Fatal(err)
	}
	fmt.Println(id, album)
    }
    err = rows.Err()
	if err != nil {
            log.Fatal(err)
	}
}
