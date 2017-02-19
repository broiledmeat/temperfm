import io
import datetime
import csv
import sqlite3


_connection = None
_cursor = None


def _get_cursor():
    global _connection, _cursor

    if _connection is None:
        from temperfm import config
        _connection = sqlite3.connect(config.cache_path, isolation_level=None)

    if _cursor is None:
        _cursor = _connection.cursor()

        # User artists in time spans
        _cursor.execute('CREATE TABLE IF NOT EXISTS user_time_span_artists (id INTEGER PRIMARY KEY AUTOINCREMENT,'
                        'name TEXT NOT NULL, start_date TIMESTAMP NOT NULL, end_date TIMESTAMP NOT NULL,'
                        'artists TEXT NOT NULL, last_accessed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)')
        _cursor.execute('CREATE INDEX IF NOT EXISTS user_time_span_artists_name_index ON user_time_span_artists(name)')
        _cursor.execute('DELETE FROM user_time_span_artists WHERE last_accessed <= DATE("now", "-30 day")')

        # Artists tags
        _cursor.execute('CREATE TABLE IF NOT EXISTS artist_tags (id INTEGER PRIMARY KEY AUTOINCREMENT,'
                        'name TEXT NOT NULL, updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, tags TEXT NOT NULL)')
        _cursor.execute('CREATE INDEX IF NOT EXISTS artist_tags_name_index ON artist_tags(name)')
        _cursor.execute('DELETE FROM artist_tags WHERE updated <= DATE("now", "-" || (7 + (ROWID % 7)) || " day")')

    return _cursor


def _to_csv(values):
    """
    :type values: list[str]
    :rtype: str
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(values)
    return buffer.getvalue().strip()


def _from_csv(value):
    """
    :type value: str
    :rtype: list[str]
    """
    buffer = io.StringIO(value)
    reader = csv.reader(buffer)
    try:
        return next(reader)
    except StopIteration:
        return []


def get_user_time_span_artists(name, start_date, end_date):
    """
    :type name: str
    :type start_date: datetime.date
    :type end_date: datetime.date
    :rtype: list[temperfm.records.ArtistPlays]
    """
    from temperfm.records import ArtistPlays

    cursor = _get_cursor()
    results = cursor.execute('SELECT rowid, artists FROM user_time_span_artists WHERE name = ? AND '
                             'start_date = ? AND end_date = ? LIMIT 1', (name, start_date, end_date)).fetchone()
    if results is not None:
        row_id, artists = results[0], _from_csv(str(results[1]))
        cursor.execute('UPDATE user_time_span_artists SET last_accessed = date("now") WHERE rowid = ? ', (row_id, ))
        return [ArtistPlays(artist, int(plays)) for artist, plays in zip(artists[0::2], artists[1::2])]


def set_user_time_span_artists(name, start_date, end_date, artists):
    """
    :type name: str
    :type start_date: datetime.date
    :type end_date: datetime.date
    :type artists: list[temperfm.records.ArtistPlays]
    """
    cursor = _get_cursor()
    values = [x for recent_artist in artists for x in [recent_artist.name, recent_artist.plays]]
    cursor.execute('INSERT INTO user_time_span_artists (name, start_date, end_date, artists)'
                   'values (?, ?, ?, ?)', (name, start_date, end_date, _to_csv(values)))


def get_artist_tags(name):
    """
    :type name: str
    :rtype: set[str] | None
    """
    cursor = _get_cursor()
    results = cursor.execute('SELECT tags FROM artist_tags WHERE name = ? ORDER BY updated DESC LIMIT 1',
                             (name, )).fetchone()
    if results is not None:
        return set(_from_csv(results[0]))


def set_artist_tags(name, tags):
    """
    :type name: str
    :type tags: set[str]
    """
    cursor = _get_cursor()
    cursor.execute('INSERT INTO artist_tags (name, tags) VALUES (?, ?)', (name, _to_csv(tags)))
