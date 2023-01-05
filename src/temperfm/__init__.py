from __future__ import annotations
import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .log import Logger
    from .profile import Profile
    from .lastfm import LastFm
    from .records import UserWeeklyArtistReport

__version__ = '0.3'


class TemperFm:
    def __init__(self, logger: Logger, profile: Profile, lastfm: LastFm):
        self._logger: Logger = logger
        self._profile: Profile = profile
        self._lastfm: LastFm = lastfm

    def _get_tags_scores(self, tags: set[str]) -> list[int]:
        scores = [0] * len(self._profile.clusters)

        for tag in tags:
            for part in tag.split():
                for i, cluster in enumerate(self._profile.clusters):
                    if part in cluster.tags:
                        scores[i] += 1

        return scores

    def get_user_weekly_artists(self, username: str, limit: int = 8) -> UserWeeklyArtistReport:
        from .records import ArtistProfileScores, UserWeeklyArtistReport

        limit = max(1, limit)
        end_date = datetime.datetime.utcnow().date()
        week_day = (end_date.weekday() + 1) % 7
        start_date = end_date - datetime.timedelta(days=week_day + ((limit - 1) * 7))

        self._logger.info(f'Generating UserWeeklyArtistsReport report for {username} from {start_date} to {end_date}')
        start_time = datetime.datetime.now()

        artists = []
        scores = set()

        for i in range(limit):
            week_start_date = start_date + datetime.timedelta(days=i * 7)
            week_end_date = min(week_start_date + datetime.timedelta(days=6), end_date)
            artists.append(self._lastfm.get_user_time_span_artists(username, week_start_date, week_end_date))

        for name in set([artist.name for artists_ in artists for artist in artists_]):
            tags = self._lastfm.get_artist_tags(name)
            scores.add(ArtistProfileScores(name, self._get_tags_scores(tags)))

        end_time = datetime.datetime.now()
        self._logger.info(f'Finished UserWeeklyArtistReport in {end_time - start_time}')

        return UserWeeklyArtistReport(username, self._profile.clusters, start_date, end_date, artists, scores)

