import json


clusters = []
""":type: list[Cluster]"""


def load(path):
    """
    :rtype: Profile
    """
    clusters.clear()

    for cluster in json.load(open(path)):
        color = cluster.get('preferred_color', None)
        if color is not None:
            color = tuple(color)
        clusters.append(Cluster(cluster['name'], set(cluster['tags']), color))


class Cluster:
    def __init__(self, name, tags, preferred_color=None):
        """
        :type name: str
        :type tags: set[str]
        :type preferred_color: tuple[float, float, float] | None
        """
        self.name = name
        self.tags = tags
        self._preferred_color = preferred_color

    @property
    def color(self):
        """
        :rtype: tuple[float, float, float]
        """
        if self._preferred_color is None:
            from random import random
            self._preferred_color = random(), random(), random()
        return self._preferred_color

    def __repr__(self):
        return f'<Cluster: {self.name}>'
