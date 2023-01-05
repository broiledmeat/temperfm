from __future__ import annotations
import json

ColorType = tuple[float, float, float]


class Cluster:
    def __init__(self, name: str, tags: set[str], preferred_color: ColorType | None = None):
        self.name: str = name
        self.tags: set[str] = tags
        self._preferred_color: ColorType | None = preferred_color

    @property
    def color(self) -> ColorType:
        if self._preferred_color is None:
            from random import random
            self._preferred_color = random(), random(), random()
        return self._preferred_color

    def __repr__(self) -> str:
        return f'<Cluster: {self.name}>'


class Profile:
    def __init__(self):
        self.clusters: list[Cluster] = []

    @staticmethod
    def load(path: str) -> Profile:
        instance = Profile()

        for cluster in json.load(open(path)):
            color = cluster.get('preferred_color', None)
            if color is not None:
                color = tuple(color)
            instance.clusters.append(Cluster(cluster['name'], set(cluster['tags']), color))

        return instance
