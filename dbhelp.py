import sqlite3


class DbHelper:

    def __init__(self, db):
        self.db = db
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artist(
                id INTEGER PRIMARY KEY, 
                url TEXT, 
                name TEXT, 
                is_new INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS song(
                id INTEGER PRIMARY KEY, 
                artist_id INTEGER, 
                url TEXT, 
                name TEXT, 
                len INTEGER,
                len_gzip INTEGER,
                lyric TEXT,
                FOREIGN KEY(artist_id) REFERENCES artist(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS letter(
                last INTEGER PRIMARY KEY
            )
        ''')
        cursor.execute('''
            INSERT INTO letter (last)
            SELECT -1 WHERE NOT EXISTS (
                SELECT * FROM letter
            )
        ''')

        db.commit()

    def get_last_letter(self):
        cursor = self.db.cursor()
        return _get_scalar(cursor, '''SELECT * FROM letter''', [0])[0]

    def set_last_letter(self, i):
        cursor = self.db.cursor()
        cursor.execute('''UPDATE letter SET last = ?''', (i,))
        self.db.commit()

    def put_artists(self, artists):
        cursor = self.db.cursor()
        cursor.executemany('''INSERT INTO artist(id, url, name) VALUES(:id, :url, :name)''', artists)
        self.db.commit()

    def put_songs(self, songs):
        try:
            cursor = self.db.cursor()
            cursor.executemany('''INSERT INTO song(id, artist_id, url, name) VALUES(:id, :artist_id, :url, :name)''',
                               songs)
            self.db.commit()
        except sqlite3.IntegrityError as e:
            print(e)

    def set_is_new(self, a, is_new):
        cursor = self.db.cursor()
        cursor.execute('''UPDATE artist SET is_new = :is_new WHERE id = :id''',
                       {"id": a["id"], "is_new": is_new})
        self.db.commit()

    def get_new_artists(self):
        cursor = self.db.cursor()
        cursor.execute('''SELECT id, url, name FROM artist WHERE is_new IS NULL''')
        return [{"id": r[0], "url": r[1], "name": r[2]} for r in cursor]

    def get_new_songs(self):
        cursor = self.db.cursor()
        cursor.execute('''SELECT id, url, name FROM song WHERE lyric IS NULL''')
        return [{"id": r[0], "url": r[1], "name": r[2]} for r in cursor]

    def set_lyric(self, s, lyric):
        cursor = self.db.cursor()
        cursor.execute('''UPDATE song SET lyric = :lyric WHERE id = :id''',
                       {"id": s["id"], "lyric": lyric})
        self.db.commit()

    def get_songs_without_gzip_len(self):
        cursor = self.db.cursor()
        cursor.execute('''SELECT id, url, name, lyric FROM song WHERE lyric IS NOT NULL and len_gzip IS NULL''')
        return [{"id": r[0], "url": r[1], "name": r[2], "lyric": r[3]} for r in cursor]

    def update_song_len(self, param):
        cursor = self.db.cursor()
        cursor.execute('''UPDATE song SET len = :len, len_gzip = :len_gzip WHERE id = :id''',
                       param)
        self.db.commit()


def _get_scalar(cursor, query, default):
    cursor.execute(query)
    r = cursor.fetchone()
    if r:
        return r
    else:
        return default
