from functools import lru_cache

import networkx as nx


class Cities:
    """ Class for keeping matrix distance and calculation distances between cities

    Parameters
    ----------
    distances: np.array
        distance matrix
    """

    def __init__(self, distances):
        graph = nx.Graph()
        for i, row in enumerate(distances):
            graph.add_node(i)
            for j, dist in enumerate(row):
                if dist:
                    graph.add_edge(i, j, weight=dist)
        self._graph = graph
        self.n = len(distances)

    @lru_cache(None)
    def get_dist(self, city1, city2):
        """ return the shortest distance and path between two cities

        Parameters
        ----------
        city1: int
        city2: int

        Returns
        -------
        result: Tuple[int, list[int]]
            The shortest distance and path

        Raises
        ------
        networkx.NetworkXNoPath: if there is no path
        WrongNode: if there is no such cities
        """
        if not (0 <= city1 < self.n) or not (0 <= city2 < self.n):
            raise WrongNode(f"Cities should be between 0 and {self.n - 1}, but they are {city1} and {city2}")
        if city1 == city2:
            raise nx.NetworkXNoPath()
        return nx.single_source_dijkstra(self._graph, city1, city2)


class WrongNode(ValueError):
    pass
