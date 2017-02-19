from temperfm.records.base import RecordBase


class ArtistProfileScores(RecordBase):
    def __init__(self, name, scores):
        """
        :type name: str
        :type scores: tuple[int, ...]
        """
        self.name = name
        self.scores = scores

    def __repr__(self):
        return f'<ArtistProfileScores: {self.name}, {self.scores}>'
