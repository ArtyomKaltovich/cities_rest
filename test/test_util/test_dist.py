import pytest
import numpy as np
from networkx import NetworkXNoPath

from util.dist import Cities


@pytest.fixture(scope="module")
def data():
    data = np.array([[0, 2, 10, 15],
                     [2, 0, 3, 6],
                     [10, 3, 0, 2],
                     [15, 6, 2, 0]], dtype=int)
    return Cities(data)


@pytest.mark.parametrize("city1, city2, expected_dist, expected_path",
                         [(1, 0, 2, [1, 0]),
                          (2, 1, 3, [2, 1])])
def test_direct(data, city1, city2, expected_dist, expected_path):
    assert (expected_dist, expected_path) == data.get_dist(city1, city2)
    expected_path = list(reversed(expected_path))
    assert (expected_dist, expected_path) == data.get_dist(city2, city1), "Symmetry check failed"


@pytest.mark.parametrize("city1, city2, expected_dist, expected_path",
                         [(0, 3, 7, [0, 1, 2, 3]),
                          (0, 2, 5, [0, 1, 2])])
def test_indirect(data, city1, city2, expected_dist, expected_path):
    assert (expected_dist, expected_path) == data.get_dist(city1, city2)
    expected_path = list(reversed(expected_path))
    assert (expected_dist, expected_path) == data.get_dist(city2, city1), "Symmetry check failed"


def test_unreachable():
    distances = np.zeros((3, 3))
    cities = Cities(distances)
    with pytest.raises(NetworkXNoPath):
        cities.get_dist(1, 2)
