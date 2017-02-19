import datetime
from temperfm.profiles import default_profile


__version__ = '0.2'


def get_user_weekly_artists(username, limit=8, profile=default_profile):
    """
    :type username: str
    :type limit: int
    :type profile: temperfm.profiles.Profile
    :rtype: UserWeeklyArtistReport
    """
    from temperfm import log
    from temperfm.records import ArtistProfileScores, UserWeeklyArtistReport
    from temperfm.profiles import get_tags_scores
    from temperfm.lastfm import get_user_time_span_artists, get_artist_tags

    limit = max(1, limit)
    end_date = datetime.datetime.utcnow().date()
    week_day = (end_date.weekday() + 1) % 7
    start_date = end_date - datetime.timedelta(days=week_day + ((limit - 1) * 7))

    log.info(f'Generating UserWeeklyArtistsReport report for {username} from {start_date} to {end_date}')
    start_time = datetime.datetime.now()

    artists = []
    scores = set()

    for i in range(limit):
        week_start_date = start_date + datetime.timedelta(days=i * 7)
        week_end_date = min(week_start_date + datetime.timedelta(days=6), end_date)
        artists.append(get_user_time_span_artists(username, week_start_date, week_end_date))

    for artist_name in set([artist.name for artists_ in artists for artist in artists_]):
        artist_scores = get_tags_scores(get_artist_tags(artist_name), profile=profile)
        scores.add(ArtistProfileScores(artist_name, artist_scores))

    end_time = datetime.datetime.now()
    log.info(f'Finished UserWeeklyArtistReport in {end_time - start_time}')

    return UserWeeklyArtistReport(username, profile, start_date, end_date, artists, scores)
