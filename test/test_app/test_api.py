import numpy as np
import pytest

from cities_rest import app, URL, X_API_KEY


@pytest.fixture(scope="module")
def data():
    data = [[0, 2, 5],
            [2, 0, 1],
            [5, 1, 0]]
    return data


@pytest.fixture(scope="module")
def auth_data():
    return {"X-API-KEY": X_API_KEY}


def test_correct(auth_data, data):
    app.init(np.array(data))
    args = _construct_args(auth_data, 0, 2)
    with app.test_client() as client:
        response = client.post(f"{URL}", data=args)
        assert b'{"body":{"distance":3,"path":[0,1,2]}}\n' == response.data
        assert 200 == response.status_code


@pytest.mark.parametrize("args", [dict(), dict(city_start=0), dict(city_finish=2)])
def test_no_param(args, auth_data, data):
    app.init(np.array(data))
    args.update(auth_data)
    with app.test_client() as client:
        response = client.post(f"{URL}", data=args)
        assert b'{"body":"Please specify city_start and city_finish arguments"}\n' == response.data
        assert 400 == response.status_code


@pytest.mark.parametrize("start, finish", [("", 10), (13, "sdas")])
def test_wrong_param(start, finish, auth_data, data):
    app.init(np.array(data))
    args = _construct_args(auth_data, start, finish)
    with app.test_client() as client:
        response = client.post(f"{URL}", data=args)
        assert b'{"body":"Cities should be integers"}\n' == response.data
        assert 400 == response.status_code


@pytest.mark.parametrize("start, finish", [(0, 10), (13, 0), (-1, -1)])
def test_wrong_node(start, finish, auth_data, data):
    app.init(np.array(data))
    args = _construct_args(auth_data, start, finish)
    with app.test_client() as client:
        response = client.post(f"{URL}", data=args)
        start_and_finish = f"{start} and {finish}"
        assert '{"body":"Cities should be between 0 and 2, but they are ' + start_and_finish + '"}\n' \
               == response.data.decode()
        assert 404 == response.status_code


@pytest.mark.parametrize("start, finish", [(0, 0), (2, 0)])
def test_no_road(start, auth_data, finish):
    data = np.zeros((3, 3))
    app.init(np.array(data))
    args = _construct_args(auth_data, start, finish)
    with app.test_client() as client:
        response = client.post(f"{URL}", data=args)
        assert b'{"body":"No road"}\n' == response.data
        assert 404 == response.status_code


@pytest.mark.parametrize("args", [dict(), dict(city_start=0, city_finish=1)])
def test_no_login(args, data):
    app.init(np.array(data))
    with app.test_client() as client:
        response = client.post(f"{URL}", data=args)
        assert b'{"body":"Please specify valid api key"}\n' == response.data
        assert 401 == response.status_code


def _construct_args(auth_data, start, finish):
    args = dict(city_start=start, city_finish=finish)
    args.update(auth_data)
    return args
