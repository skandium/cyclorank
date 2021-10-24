import json
import pickle
import random
import os
from functools import partial

import pyproj
from shapely.geometry import Point, shape, Polygon
from shapely.ops import transform

from city_conf import city_mappings

proj_wgs84 = pyproj.Proj('+proj=longlat +datum=WGS84')

NUM_POINTS = 1000
NUM_ROUTES = 500
CIRCLE_RADIUS_KM = 7.5


def random_points_within(circle_polygon, city_polygon, num_points):
    min_x, min_y, max_x, max_y = circle_polygon.bounds

    points = []

    while len(points) < num_points:
        random_point = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
        if random_point.within(circle_polygon):
            if random_point.within(city_polygon):
                points.append(random_point)

    return points


def geodesic_point_buffer(lat, lon, km):
    # Azimuthal equidistant projection
    aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
    project = partial(
        pyproj.transform,
        pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)),
        proj_wgs84)
    buf = Point(0, 0).buffer(km * 1000)  # distance in metres
    return transform(project, buf).exterior.coords[:]


def create_circle_around_coord(lat, lon, km):
    b = geodesic_point_buffer(lat, lon, km)
    circle_lats = [x[1] for x in b]
    circle_lngs = [x[0] for x in b]
    return circle_lats, circle_lngs, b


def load_city_shapes(city_name):
    with open(f"city_polygons/{city_name.lower()}_polygon.geojson") as f:
        city_json = json.load(f)

    city_polygon = city_json["geometries"][0]
    city_shape = shape(city_polygon)

    with open(f"city_polygons/{city_name.lower()}.geojson") as f:
        city_json = json.load(f)

    city_centroid_shape = shape(city_json)
    city_centroid = Point((city_centroid_shape.centroid.y, city_centroid_shape.centroid.x))

    xx, yy = city_centroid.x, city_centroid.y

    circle_lats, circle_lngs, b = create_circle_around_coord(yy, xx, 7.5)

    circle_polygon = Polygon(b)

    shapes = {
        "circle_polygon": circle_polygon,
        "city_polygon": city_shape,
        "city_centroid": city_centroid,
        "circle_lats": circle_lats,
        "circle_lngs": circle_lngs,
        "centroid_x": xx,
        "centroid_y": yy
    }

    return shapes


if __name__ == "__main__":
    for country_map in city_mappings:
        for city in city_mappings[country_map]:
            city_name = list(city.keys())[0]
            try:
                if not os.path.exists(f"routing/routes/{city_name}.p"):
                    print(city_name)
                    shapes = load_city_shapes(city_name)
                    points = random_points_within(circle_polygon=shapes["circle_polygon"],
                                                  city_polygon=shapes["city_polygon"],
                                                  num_points=NUM_POINTS)
                    routes = []
                    for i in range(NUM_ROUTES):
                        start_point = random.choice(points)
                        end_point = random.choice(points)
                        routes.append(
                            (float(start_point.y), float(start_point.x), float(end_point.y), float(end_point.x)))

                    with open(f"routing/routes/{city_name}.p", "wb") as f:
                        pickle.dump(routes, f)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(e)
                continue
