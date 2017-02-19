import time
import datetime
import re
import requests


def query(**kwargs):
    """
    :rtype: dict[str, Any]
    """
    from temperfm import config, log

    for key, value in kwargs.items():
        if key.endswith('_'):
            del kwargs[key]
            key = key[:-1]
            kwargs[key] = value
        if isinstance(value, (datetime.datetime, datetime.date)):
            kwargs[key] = int(time.mktime(value.timetuple()))

    log.debug(f'Querying LastFM {kwargs}')

    kwargs.update({'api_key': config.lastfm_key, 'format': 'json'})

    result = requests.get('https://ws.audioscrobbler.com/2.0', params=kwargs).json()

    if 'message' in result and result['message'].startswith('Invalid API key'):
        raise RuntimeError(f'Invalid Last.fm API key: {config.lastfm_key}')

    return result


def get_user_top_recent_artists(name, period='1month', limit=16):
    """
    :type name: str
    :type period: str
    :type limit: int
    :rtype: list[ArtistPlays]
    """
    from temperfm.records import ArtistPlays

    artists = []
    results = query(method='user.gettopartists', user=name, period=period, limit=limit)
    for artist in results['topartists']['artist']:
        artists.append(ArtistPlays(artist['name'], artist['playcount']))
    return artists


def get_user_time_span_artists(name, start_date, end_date=None):
    """
    :type name: str
    :type start_date: datetime.date
    :type end_date: datetime.date | None
    :rtype: list[ArtistPlays]
    """
    from temperfm.lastfm import cache
    from temperfm.records import ArtistPlays

    if end_date is None:
        end_date = start_date + datetime.timedelta(days=6)

    # Do not request the cache if it spans the current date
    if not (start_date <= datetime.datetime.utcnow().date() <= end_date):
        artists = cache.get_user_time_span_artists(name, start_date, end_date)
        if artists is not None:
            return artists

    # Dates get converted to timestamps, which will result in end_date representing the beginning of the last day,
    # rather than the end. So convert the date to a datetime, and add the missing time span.
    end_datetime = datetime.datetime(end_date.year, end_date.month, end_date.day) + \
        datetime.timedelta(days=1, seconds=-1)

    artists = []
    results = query(method='user.getweeklyartistchart', user=name,
                    from_=start_date, to=end_datetime)
    for artist in results['weeklyartistchart']['artist']:
        artists.append(ArtistPlays(artist['name'], int(artist['playcount'])))

    cache.set_user_time_span_artists(name, start_date, end_date, artists)

    return artists


def get_artist_tags(name):
    """
    :type name: str
    :rtype: set[str]
    """
    from temperfm.lastfm import cache

    tags = cache.get_artist_tags(name)
    if tags is not None:
        return tags

    tags = set()
    valid_chars = re.compile('[^\w]')

    results = query(method='artist.gettoptags', artist=name)
    for tag in results['toptags']['tag']:
        tag = valid_chars.sub(' ', tag['name']).lower()
        tags.add(tag)

    cache.set_artist_tags(name, tags)

    return tags
