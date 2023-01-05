from __future__ import annotations
import io
import datetime
import csv
import sqlite3
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from ..records import ArtistPlays


class LastFmCache:
    def __init__(self, filepath: str):
        self._filepath: str = filepath

        self._connection = None
        self._cursor = None

    def _get_cursor(self):
        if self._connection is None:
            self._connection = sqlite3.connect(self._filepath, isolation_level=None)

        if self._cursor is None:
            self._cursor = self._connection.cursor()

            # User artists in time spans
            self._cursor.execute(
                'CREATE TABLE IF NOT EXISTS user_time_span_artists (id INTEGER PRIMARY KEY AUTOINCREMENT,'
                'name TEXT NOT NULL, start_date TIMESTAMP NOT NULL, end_date TIMESTAMP NOT NULL,'
                'artists TEXT NOT NULL, last_accessed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)')
            self._cursor.execute(
                'CREATE INDEX IF NOT EXISTS user_time_span_artists_name_index ON user_time_span_artists(name)')
            self._cursor.execute('DELETE FROM user_time_span_artists WHERE last_accessed <= DATE("now", "-30 day")')

            # Artists tags
            self._cursor.execute('CREATE TABLE IF NOT EXISTS artist_tags (id INTEGER PRIMARY KEY AUTOINCREMENT,'
                                 'name TEXT NOT NULL, updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, tags TEXT NOT NULL)')
            self._cursor.execute('CREATE INDEX IF NOT EXISTS artist_tags_name_index ON artist_tags(name)')
            self._cursor.execute(
                'DELETE FROM artist_tags WHERE updated <= DATE("now", "-" || (7 + (ROWID % 7)) || " day")')

        return self._cursor

    @staticmethod
    def _to_csv(values: Iterable[str]) -> str:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(values)
        return buffer.getvalue().strip()

    @staticmethod
    def _from_csv(value: str) -> list[str]:
        buffer = io.StringIO(value)
        reader = csv.reader(buffer)
        try:
            return next(reader)
        except StopIteration:
            return []

    def get_user_time_span_artists(self, name: str, start_date: datetime, end_date: datetime) -> list[ArtistPlays]:
        from ..records import ArtistPlays

        cursor = self._get_cursor()
        results = cursor.execute('SELECT rowid, artists FROM user_time_span_artists WHERE name = ? AND '
                                 'start_date = ? AND end_date = ? LIMIT 1', (name, start_date, end_date)).fetchone()
        if results is not None:
            row_id, artists = results[0], self._from_csv(str(results[1]))
            cursor.execute('UPDATE user_time_span_artists SET last_accessed = date("now") WHERE rowid = ? ', (row_id,))
            return [ArtistPlays(artist, int(plays)) for artist, plays in zip(artists[0::2], artists[1::2])]

    def set_user_time_span_artists(self,
                                   name: str,
                                   start_date: datetime,
                                   end_date: datetime,
                                   artists: list[ArtistPlays]):
        cursor = self._get_cursor()
        values = [x for recent_artist in artists for x in [recent_artist.name, recent_artist.plays]]
        cursor.execute('INSERT INTO user_time_span_artists (name, start_date, end_date, artists)'
                       'values (?, ?, ?, ?)', (name, start_date, end_date, self._to_csv(values)))

    def get_artist_tags(self, name: str) -> set[str] | None:
        cursor = self._get_cursor()
        results = cursor.execute('SELECT tags FROM artist_tags WHERE name = ? ORDER BY updated DESC LIMIT 1',
                                 (name,)).fetchone()
        if results is not None:
            return set(self._from_csv(results[0]))

    def set_artist_tags(self, name: str, tags: set[str]):
        cursor = self._get_cursor()
        cursor.execute('INSERT INTO artist_tags (name, tags) VALUES (?, ?)', (name, self._to_csv(tags)))
