import os
import json


DEFAULT_PROFILE_PATH = os.path.join(os.path.dirname(__file__), 'default_profile.json')


class Profile:
    def __init__(self, path):
        """
        :type path: str
        """
        self.clusters = []
        """:type: list[Cluster]"""

        for cluster in json.load(open(path)):
            color = cluster.get('preferred_color', None)
            if color is not None:
                color = tuple(color)
            self.clusters.append(Cluster(cluster['name'], set(cluster['tags']), color))


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
