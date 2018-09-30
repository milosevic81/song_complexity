import sqlite3
import string
import zlib

from progress.bar import Bar

import dbhelp
import soaphelp

"""
scrap https://tekstovi.net/2,E,0.html
for each letter get artist
for each artist get songs
for each song get lyrics
"""

db = sqlite3.connect('lyrics.db')


def main():
    soap = soaphelp.Soap()
    sql = dbhelp.DbHelper(db)

    # calculate compressed length
    song_raw = sql.get_songs_without_gzip_len()
    bar = Bar('Calculate compressed size', suffix='[%(index)d|%(max)d] avg %(avg)ds eta %(eta_td)s', max=len(song_raw))
    for s in song_raw:
        cmpstr = zlib.compress(s["lyric"].encode('utf-8'))
        sql.update_song_len({
            "id": s["id"],
            "len": len(s["lyric"]),
            "len_gzip": len(cmpstr)})
        bar.next()

    # get names of all artists
    letter = sql.get_last_letter() + 1
    for i, c in enumerate(string.ascii_uppercase[letter:]):
        a = soap.get_artists(c)
        sql.put_artists(a)
        sql.set_last_letter(letter + i)

    # get songs for artists
    artists = sql.get_new_artists()
    if artists:
        bar = Bar('Get songs', suffix='[%(index)d|%(max)d] avg %(avg)ds eta %(eta_td)s', max=len(artists))
        for a in artists:
            songs = soap.get_songs(a)
            sql.put_songs(songs)
            sql.set_is_new(a, False)
            bar.next()

    # get lyrics for all songs
    songs = sql.get_new_songs()
    if songs:
        bar = Bar('Get lyrics', suffix='[%(index)d|%(max)d] avg %(avg)ds eta %(eta_td)s', max=len(songs))
        for s in songs:
            lyric = soap.get_lyric(s)
            sql.set_lyric(s, lyric)
            bar.next()


if __name__ == '__main__':
    main()
