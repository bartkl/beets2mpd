# `beets2mpd`
This script generates a MPD tag cache file from a Beets database.

This enables MPD tag caching sourced from the beets library database instead of from the audio file tags.

Has only been used on Linux so far, but it should work on Windows and Mac as well.

Windows paths for music files are supported and tested.

## Installation
_TODO_.


## How to use
_TODO_.

## Purpose
This script is for people who use Beets to manage their music library, and wish to generate an MPD tag cache file from the Beets database.

The reasons that motivated me to want this, are:

1. _I do not want to make modifications to my music files, i.e. no file renames or tag writes_.
    - Among my reasons for this is that this allows for more efficiency backing up. For example, changing a single tag value will trigger a full copy of that file during backup. This means that if you change a lot of tags, say by renaming a genre, that backing up those files will potentially take a very long time.
2. _I want to be able to use multiple genres per song or album_.
    - MPD supports this, but Beets does not (yet, see [#505](https://github.com/beetbox/beets/issues/505). This script will parse multiple genres from the `genre` field in the Beets database by a delimiter that you can choose yourself, and write these to the tagcache file.

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
This script originally was written by reverse engineering what my MPD tag cache file looked like, but since then I have read the MPD source code to make sure it conforms. During this process, I discovered that my implementation has the following limitations:

* Only regular files are supported, so no archives, containers or playlists.

## Caveats
* The biggest issue is that as soon as you or some of your MPD clients triggers a database reload, this will regenerate the tag cache using the original audio file tags source. This means that to use this solution stably, you must make sure such a reload never gets triggered.
    - This sounds like a major limitation/issue, but I have easily worked around it for the last few years. The clients I used were ncmpcpp, mpc, and MPDroid.
    - Newer versions of MPD have automatic database updating based on file changes. Because of this limitation, you won't be able to do that. However, writing your own scripts to mimic this feature is fairly doable.
* The format of the generated tagcache file is not based on any technical specification, but on my reverse engineering of what the file's structure is like. This is not ideal, but I have been using this script for some years now, and it is has never generated a corrupt or faulty file.
* This plugin has been created for personal use only and possibly needs work to perform on other devices and installations.

## Roadmap
Although the code is pretty optimized, Python is relatively slow nonetheless. For low-resource devices such as SoC's like the Raspberry Pi, this script can take seconds on large libraries.

Options:
* Redo the entire implementation in C. (Prefered)
* Leverage performance gains by using Cython.
