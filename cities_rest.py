import argparse

import numpy as np
from flask import Flask, jsonify, request
from networkx import NetworkXNoPath

from util.dist import Cities, WrongNode

APP_NAME = "cities_rest"
API_VERSION = "v1.0"
URL = f"/{APP_NAME}/api/{API_VERSION}/"
X_API_KEY = "123321"
PATH_TO_DATA_FILE = "data/matrix_distance"


class CitiesApp(Flask):
    def __init__(self, import_name):
        super().__init__(import_name)
        self.distances = None

    def init(self, distances):
        self.distances = Cities(distances) if not isinstance(distances, str)\
            else Cities(np.load(open(distances, "rb")))


app = CitiesApp(__name__)


@app.route('/')
def index():
    return "Rest service for finding shortest way between two cities."


@app.route(URL, methods=["POST"])
def dist_query():
    no_auth = _auth()
    if no_auth:
        response, status_code = no_auth
    else:
        response, status_code = _process_dist_query()
    return jsonify({"body": response}), status_code


def _process_dist_query():
    city_start = request.form.get("city_start")
    city_finish = request.form.get("city_finish")
    try:  # it is better to ask for forgiveness than permission
        city_start = int(city_start)
        city_finish = int(city_finish)
    except ValueError:
        status_code = 400
        response = "Cities should be integers"
    except TypeError:
        status_code = 400
        response = "Please specify city_start and city_finish arguments"
    else:
        response, status_code = _find_path(city_start, city_finish)
    return response, status_code


def _auth():
    auth = request.form.get("X-API-KEY")
    if auth != X_API_KEY:
        status_code = 401
        response = "Please specify valid api key"
        return response, status_code


def _find_path(city_start, city_finish):
    try:
        dist, path = app.distances.get_dist(city_start, city_finish)
        response = dict(path=path, distance=int(dist))
        status_code = 200
    except NetworkXNoPath:
        response = "No road"
        status_code = 404
    except WrongNode as e:
        status_code = 404
        response = str(e)
    return response, status_code


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="REST service for calculation shortest path between two cities.\n"
                                                 f"Usage: send POST request to {URL}, and specify the following "
                                                 f"arguments: city_start, city_finish and api key")
    parser.add_argument("--debug-mode", action="store_true",
                        help="Run server in debug mode, specify 1 or True to for it.")

    args = parser.parse_args()
    app.init(PATH_TO_DATA_FILE)
    app.run(debug=args.debug_mode)
