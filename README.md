# `beets2mpd`
This script generates a MPD tag cache file from a Beets database. It enables MPD tag caching sourced from the beets library database instead of from the audio file tags.

It has only been used on Linux so far, but it should work on Windows and Mac as well. Windows paths for music files are supported and tested.

## Installation
Make sure you have Python 3.7 or higher installed. Other than that, there are no dependencies. Making it work for older versions of Python is not too much work. If you need help, feel free to contact me.

Then, copy the `beets2mpd.py` file somewhere you like. That's all there's to it.

If you want to be able to invoke the script directly, make sure the shebang line correctly identifies your Python interpreter, and the excution bit is set on the file.

Personally, I have renamed the file to `beets2mpd`, made it executable and placed it in `/usr/local/bin`.

## How to use
### Configuration
There is no config file, because I wanted to keep things simple and performant, so configuration is done through changing some variables in the `beets2mpd.py` file. At the top of that file, you'll find the following variables to tweak:

- `MUSIC_ROOT_DIR`: This should point to the base path of your music library files. This path is subtracted from the `path` field of all items in the Beets database, so that they are relative to this base dir. Then, in your MPD config the `music_directory` setting should also point to this base path, and all should be well.
    - Note: this path should be provided in absolute form.
    - When using Windows path, make sure the backslashes are escaped, i.e. `'C:\\Music'`. You can also use raw strings, i.e. `r'C:\Music'`.
    - Finally, MPD is capable of following symlinks. Speaking of which: I highly recommend letting Beets create symlinks on which it can do renaming and directory ordering. This creates a separate, ordered library on your file system without touching the original files, and the metadata is provided by Beets through the tag cache generated by this script.
- `BEETS_DB_FILEPATH`: The path to your Beets database file.
- `TAGCACHE_FILEPATH`:  The path to the output tagcache file. It's up to you whether this is immediately the real MPD tagcache file in use, or some intermediate.
- `GENRE_DELIMITER`: A string that delimites multiple genre values in the `genre` field. How this can be used is described in _Multiple genres_.
- `MPD_VERSION`: The version of MPD on the system.
- `MPD_DB_FORMAT`: An integer that encodes the format of the tag cache file. Unless you know what you're doing, don't change this value.

### Running the script
When all configuration is in place, it's as simple as running the script:

```sh
$ beets2mpd
```

It reads the supplied Beets database, optionally splits genre values by the provided delimiter value, and writes to the given MPD tagcache path.

When you use this tag cache file in MPD, it should work.

### Multiple genres
If you want to use multiple genres, you have to choose a character or string to delimit your genre values with. Set the `GENRE_DELIMITER` variable in `beets2mpd.py` accordingly. Now, when you assign multiple genre values to the `genre` field delimited by that string, the script will understand the purpose and when ran, will split the values so that those are each a genre assigned to the item in the tag cache.

For example. Let's say we use the genre delimiter `|`, and we set the `genre` value for some album or item in Beets to `Ambient|Neo-Classical`, then this script will split these values into `Ambient` and `Neo-Classical` and write both of these to the tagcache for that entry.

## Purpose
This script is for people who use Beets to manage their music library, and wish to generate an MPD tag cache file from the Beets database.

The reasons that motivated me to want this, are:

1. _I do not want to make modifications to my music files, i.e. no file renames or tag writes_.
    - Among my reasons for this is that this allows for more efficiency backing up. For example, changing a single tag value will trigger a full copy of that file during backup. This means that if you change a lot of tags, say by renaming a genre, that backing up those files will potentially take a very long time.
2. _I want to be able to use multiple genres per song or album_.
    - MPD supports this, but Beets does not (yet, see [#505](https://github.com/beetbox/beets/issues/505)). This script will parse multiple genres from the `genre` field in the Beets database by a delimiter that you can choose yourself, and write these to the tagcache file.

(For those who think: why not use Beets's BPD plugin, please read the section _Why not BPD_ below.)

If you **can** modify your music files, the setup is usually pretty straight-forward. You simply import music into Beets, perhaps make some manual modifications to the metadata as well, and make sure Beets is configured to write these changes to the files' tags, directory names and filenames. This way, MPD will generate its tag cache from those file tags, and everything is fine. If you ever find yourself changing file tags using tag editing software, no problem. You tell Beets to update its database and it will update those changes.

However, if you can't, you have to alter your setup to make things work right. Before I thought of this script, what I'd do is configure Beets to copy imported files to a designated library directory, and then apply the writes on those files.

This is a clean solution, but it has drawbacks:

* It makes importing a lot slower due to the copying of potentially large amounts of data.
* It's costly on storage to have to duplicate all your files.

### Why not BPD
Beets's BPD plugin is a partial implementation of the MPD protocol which uses the Beets DB for music metadata, instead of the tag cache which is generated from the audio files's tags.

In many ways this is preferable to the solution this script enables you with, but it is a lot of work to maintain such an implementation, which is proven by the fact that BPD is already heavily outdated. Also, it is hard to do well, and I find BPD's performance to be very poor, whereas the original MPD performs flawlessly.

The solution I envisioned is simpler: use the original MPD, but provide it with a tag cache from a different source which is based on the Beets database. This script does exactly that: it reads a Beets database, and generates an MPD tag cache file.

## Limitations
This script originally was written by reverse engineering what my MPD tag cache file looked like. So far I'm aware of the following limitations of my implementation:

* Only regular files are supported, so no archives, containers or playlists.

## Caveats
* The biggest issue is that as soon as you or some of your MPD clients triggers a database reload, this will regenerate the tag cache using the original audio file tags source. This means that to use this solution stably, you must make sure such a reload never gets triggered.
    - This sounds like a major limitation/issue, but I have easily worked around it for the last few years. The clients I used were ncmpcpp, mpc, and MPDroid.
    - Newer versions of MPD have automatic database updating based on file changes. Because of this limitation, you won't be able to do that. However, writing your own scripts to mimic this feature is fairly doable.
* The format of the generated tagcache file is not based on any technical specification, but on my reverse engineering of what the file's structure is like. This is not ideal, but I have been using this script for some years now, and it is has never generated a corrupt or faulty file.
* The script reads directly from Beets's database, instead of through the API. This is bad practice, and it can or could lead to issues. The API is [terribly slow however](https://github.com/beetbox/beets/issues/2388), so that's why I chose to go this route. So far I have not encountered issues.
* This plugin has been created for personal use only and possibly needs work to perform on other devices and installations.

## Roadmap
Although the code is already pretty optimized (if you were wondering why it is so devoid of structure and extremely iterative, this is why), Python is relatively slow nonetheless. For low-resource devices such as SoCs like the Raspberry Pi, this script can take seconds on large libraries.

Options:
* Redo the entire implementation in C. (Prefered)
* Leverage performance gains by using Cython.
