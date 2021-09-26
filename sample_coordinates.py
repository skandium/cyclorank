import numpy as np
import random
import json
import subprocess
import pickle

from shapely.geometry import Point, shape
from geoflow.utils import stopwatch
from geoflow.spatial import haversine

city_name = "amsterdam"

with open(f"city_polygons/{city_name}.geojson") as f:
    city_json = json.load(f)

city_polygon = shape(city_json)

NUM_POINTS = 1000
NUM_ROUTES = 500


def prepare_map(city_name):
    pass


@stopwatch()
def random_points_within(poly, num_points):
    min_x, min_y, max_x, max_y = poly.bounds

    points = []

    while len(points) < num_points:
        random_point = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
        if (random_point.within(poly)):
            points.append(random_point)

    return points


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


@stopwatch()
def sample_distributional_points_from_uniform(poly, uniform_points):
    centroid = poly.centroid
    centroid_lat, centroid_lng = centroid.y, centroid.x

    lats = []
    lngs = []
    for pt in uniform_points:
        lats.append(pt.y)
        lngs.append(pt.x)

    distances = haversine(centroid_lat, centroid_lng, lats, lngs)


if __name__ == "__main__":
    points = random_points_within(city_polygon, NUM_POINTS)
    routes = []
    for i in range(NUM_ROUTES):
        start_point = random.choice(points)
        end_point = random.choice(points)
        routes.append((float(start_point.y), float(start_point.x), float(end_point.y), float(end_point.x)))

    with open(f"routes/{city_name}.p", "wb") as f:
        pickle.dump(routes, f)
