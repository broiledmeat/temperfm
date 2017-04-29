import time
import datetime
import json
from .base import RecordBase


class UserWeeklyArtistReport(RecordBase):
    def __init__(self, name, clusters, start_date, end_date, artists, scores):
        """
        :type name: str
        :type clusters: list[temperfm.profile.Cluster]
        :type start_date: datetime.date
        :type end_date: datetime.date
        :type artists: list[list[temperfm.records.ArtistPlays]]
        :type scores: set[temperfm.records.ArtistProfileScores]
        """
        self.name = name
        self.clusters = clusters
        self.start_date = start_date
        self.end_date = end_date
        self.artist_weekly = artists
        self.artist_profile_scores = scores

    def to_json(self):
        return json.dumps({
            'username': self.name,
            'start_date': int(time.mktime(self.start_date.timetuple())),
            'end_time': int(time.mktime(self.end_date.timetuple())),
            'clusters': [cluster.name for cluster in self.clusters],
            'artists': {
                'scores': {artist.name: artist.scores for artist in self.artist_profile_scores},
                'weekly': [
                    {
                        'date': int(time.mktime((self.start_date + datetime.timedelta(days=i * 7)).timetuple())),
                        'artists': {artist.name: artist.plays for artist in weekly}
                    }
                    for i, weekly in enumerate(self.artist_weekly)]
            }
        })

    def __repr__(self):
        cluster_names = [cluster.name for cluster in self.clusters]
        return f'<UserWeeklySpanArtistReport: {self.name}, {self.start_date}, {self.end_date}, {cluster_names},' \
               f'{self.artist_profile_scores}'
