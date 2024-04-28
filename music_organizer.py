# Peter McFarlane
# 2024

import os
import re
from pathlib import Path
from tinytag import TinyTag, TinyTagException

# put names of origin and destinaiton directories here
root_dir = '<paste root directory here>'
dest_dir = '<paste destination directory here>'

# filepath formatting
root_dir.replace(os.sep, '/')
dest_dir.replace(os.sep, '/')
if (root_dir[-1] != '/'):
    root_dir += '/'
if (dest_dir[-1] != '/'):
    dest_dir += '/'

# generate list of all filepaths in the root directory and its subdirectories
paths = Path(root_dir).rglob('*')

supported_extensions = set(TinyTag.SUPPORTED_FILE_EXTENSIONS)

# dictionary to map articles to title case instead of proper case
articles = {
    ' A ': ' a ',
    ' In ': ' in ',
    ' Of ': ' of ',
    ' On ': ' on ',
    ' Or ': ' or ',
    ' To ': ' to ',  
    ' And ': ' and ',
    ' The ': ' the ' 
}

# accepts/returns string of an artist/album/song name
def string_formatter(name):
    # strip whitespace 
    name = name.strip() 
    # remove oddball characters that can't be used in filenames
    name = re.sub('[<>:?|/\*"]', '', name) 
    # change articles to be title case rather than proper case
    # e.g. "System Of A Down" -> "System of a Down"
    for k, v in articles.items(): 
        name = name.replace(k, v)

    return name

# accepts a list of all song paths within the root directory and all subdirectories
def organize_songs(paths):
    num_organized = 0
    num_skipped = 0

    print('\norganizing...')

    for path in paths:
        extension = os.path.splitext(path)[1]
        if extension in supported_extensions:
            try:
                # METADATA
                track = TinyTag.get(path)

                # TITLE
                if track.title != None and len(track.title) != 0:
                    title = string_formatter(track.title)
                else:
                    title = path.stem

                # ARTIST
                if track.artist != None and len(track.artist) != 0:
                    artist = string_formatter(track.artist)
                else:
                    artist = '~ No artist'
                    # keep songs called "Track XX" that have no artist from overwriting each other
                    if title[:6] == 'Track ':
                        title = path.stem
                    
                # move "The" to the end so as to not screw up alphabetization
                # e.g. "The Cardigans" -> "Cardigans, The"
                if artist[:4] == 'The ':
                    artist = artist[4:] + ', The'

                # create artist folder
                Path(dest_dir + artist).mkdir(parents=True, exist_ok=True)

                # ALBUM
                if track.album != None and len(track.album) != 0:
                    album = string_formatter(track.album)

                    # create album folder
                    Path(dest_dir + artist + '/' + album).mkdir(parents=True, exist_ok=True)

                    # move song to that album folder
                    try:
                        os.rename(path, dest_dir + artist + '/' + album + '/' + title + extension)
                        num_organized += 1
                    except:
                        num_skipped += 1
                        continue

                # plop song directly into artist folder if there's no album data
                else:
                    try:
                        os.rename(path, dest_dir + artist + '/' + title + extension)
                        num_organized += 1
                    except:
                        num_skipped += 1
                        continue

            # just move on to the next song if TinyTag yells at us
            except TinyTagException:
                num_skipped += 1
                continue
            
    print('\ndone :)')
    print('songs organized: ', num_organized)
    print('songs skipped:   ', num_skipped)

# main loop
organize_songs(paths)