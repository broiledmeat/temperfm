from __future__ import annotations
import time
import datetime
import re
import requests
from .cache import LastFmCache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..log import Logger
    from ..records import ArtistPlays


class LastFm:
    def __init__(self, key: str, logger: Logger, cache: LastFmCache):
        self._key: str = key
        self._logger: Logger = logger
        self._cache: LastFmCache = cache

    def query(self, **kwargs) -> dict:
        params = {}

        for key, value in kwargs.items():
            if key.endswith('_'):
                key = key[:-1]
            if isinstance(value, (datetime.datetime, datetime.date)):
                value = int(time.mktime(value.timetuple()))
            params[key] = value

        self._logger.debug(f'Querying LastFM {kwargs}')

        params['api_key'] = self._key
        params['format'] = 'json'

        result = requests.get('https://ws.audioscrobbler.com/2.0', params=params).json()

        if 'message' in result and result['message'].startswith('Invalid API key'):
            raise RuntimeError(f'Invalid Last.fm API key: {self._key}')

        return result

    def get_user_top_recent_artists(self, name: str, period: str = '1month', limit: int = 16) -> list[ArtistPlays]:
        from ..records import ArtistPlays

        artists = []
        results = self.query(method='user.gettopartists', user=name, period=period, limit=limit)
        for artist in results['topartists']['artist']:
            artists.append(ArtistPlays(artist['name'], artist['playcount']))
        return artists

    def get_user_time_span_artists(self,
                                   name: str,
                                   start_date: datetime,
                                   end_date: datetime | None = None
                                   ) -> list[ArtistPlays]:
        from ..records import ArtistPlays

        if end_date is None:
            end_date = start_date + datetime.timedelta(days=6)

        # Do not request the cache if it spans the current date
        if not (start_date <= datetime.datetime.utcnow().date() <= end_date):
            artists = self._cache.get_user_time_span_artists(name, start_date, end_date)
            if artists is not None:
                return artists

        # Dates get converted to timestamps, which will result in end_date representing the beginning of the last day,
        # rather than the end. So convert the date to a datetime, and add the missing time span.
        end_datetime = (datetime.datetime(end_date.year, end_date.month, end_date.day) +
                        datetime.timedelta(days=1, seconds=-1))

        artists = []
        results = self.query(method='user.getweeklyartistchart', user=name, from_=start_date, to=end_datetime)
        for artist in results['weeklyartistchart']['artist']:
            artists.append(ArtistPlays(artist['name'], int(artist['playcount'])))

        self._cache.set_user_time_span_artists(name, start_date, end_date, artists)

        return artists

    def get_artist_tags(self, name: str) -> set[str]:
        tags = self._cache.get_artist_tags(name)
        if tags is not None:
            return tags

        tags = set()
        valid_chars = re.compile(r'\W')

        results = self.query(method='artist.gettoptags', artist=name)
        for tag in results['toptags']['tag']:
            tag = valid_chars.sub(' ', tag['name']).lower()
            tags.add(tag)

        self._cache.set_artist_tags(name, tags)

        return tags
