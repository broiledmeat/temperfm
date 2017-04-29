from .base import RecordBase


class ArtistPlays(RecordBase):
    def __init__(self, name, plays):
        """
        :type name: str
        :type plays: int
        """
        self.name = name
        self.plays = plays

    def __repr__(self):
        return f'<ArtistPlays: {self.name}, {self.plays}>'
