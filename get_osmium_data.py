"""
Extract all objects with an amenity tag from an osm file and list them
with their name and position.
This example shows how geometries from osmium objects can be imported
into shapely using the WKBFactory.
"""
import osmium as o
import numpy as np
import sys
import pickle
import json

from shapely.geometry import shape, Point

from geoflow.utils import stopwatch
from geoflow.spatial import haversine


class AmenityListHandler(o.SimpleHandler):
    def __init__(self, city_centroid, decay_conf=None):
        super(AmenityListHandler, self).__init__()
        self.total_road_length = 0
        self.total_cycling_road_length = 0
        self.total_cycle_lane_length = 0
        self.total_cycle_track_length = 0
        self.total_cycle_road_misc_length = 0

        self.city_centroid = city_centroid
        self.road_distances_from_centroid = []

        self.parking_counter = 0

        self.decay_conf = decay_conf

    def apply_weight_decay(self, road_distance, road_distance_from_centroid):
        effective_distance = np.minimum(np.maximum(road_distance_from_centroid - self.decay_conf["lower_threshold"], 0),
                                        self.decay_conf["upper_threshold"])

        distance_weight = np.exp(
            self.decay_conf["decay_coef"] * effective_distance)

        # print(road_distance)
        # print(road_distance_from_centroid)
        adj_dist = distance_weight * road_distance
        # print(adj_dist)
        # if road_distance_from_centroid > 2:
        #     raise ValueError
        return adj_dist

    def parse_way_data(self, w):
        """Based on https://wiki.openstreetmap.org/wiki/Bicycle"""
        if 'highway' in w.tags:
            # print(w.id)
            # print(w.nodes)
            # print(w.nodes[0].lat)
            # raise ValueError

            # How to modify distances:
            # 2 way road with 2 way cycletrack or 2 cycletracks on both sides - 0.5 multiplier for cycleway
            # 1 way road with 2 way cycletrack - 0.5 multiplier for road
            # 2 way road with 1 way cycletrack - 0.5 multiplier for cycleway
            # 2 way road with 2 lanes - no multipliers
            # 2 way road with 1 lane - 0.5 multiplier on lane (???)
            # 1 way road with 2 lanes - 0.5 mult for road
            # 1 way road with 1 lane - 0.5 mult for both
            # 1 way road, 2 way lane - 0.5 mult for road
            # 1 way road with 1 lane - 0.5 mult for both

            road_length = o.geom.haversine_distance(w.nodes)
            first_node = w.nodes[0]
            road_distance_from_centroid = haversine(first_node.lat, first_node.lon, self.city_centroid.y,
                                                    self.city_centroid.x)
            self.road_distances_from_centroid.append(road_distance_from_centroid)

            cycle_lane_length = 0
            cycle_track_length = 0
            cycle_road_misc_length = 0

            # Discount oneways
            oneway = False
            if ("oneway" in w.tags) and (w.tags["oneway"] == "yes"):
                road_length = 0.5 * road_length
                oneway = True

            # Cycle lanes
            if (
                    # L1a, L1b, M1, M2a, M2b, M2c, B2
                    (("cycleway" in w.tags) and (w.tags["cycleway"] == "lane")) or
                    # L1a, L1b, L2, M1, M2a, M2d, M3b, S2
                    (("cycleway:right" in w.tags) and (w.tags["cycleway:right"] == "lane")) or
                    # L1a, L1b, M1, M2b, M2d, M3a
                    (("cycleway:left" in w.tags) and (w.tags["cycleway:left"] == "lane")) or
                    # L1a
                    (("cycleway:both" in w.tags) and (w.tags["cycleway:both"] == "lane")) or
                    # M3a
                    (("cycleway" in w.tags) and (w.tags["cycleway"] == "opposite_lane")) or
                    # B1
                    ("bicycle:lanes" in w.tags) or
                    # B3
                    (("cycleway:right" in w.tags) and (w.tags["cycleway:right"] == "share_busway")) or
                    (("cycleway:left" in w.tags) and (w.tags["cycleway:left"] == "share_busway"))
            ):
                if oneway:
                    if ("oneway:bicycle" in w.tags) and (w.tags["oneway:bicycle"] == "no"):
                        # TODO this fails for S1, B6, M3a, M3b
                        # TODO if clause for M3a/M3b
                        cycle_lane_length = road_length * 2
                    else:
                        cycle_lane_length = road_length
                else:
                    cycle_lane_length = road_length

            # Cycle tracks
            if (
                    # S5?
                    ((w.tags["highway"] == "cycleway") and ("oneway" not in w.tags)) or
                    # T1, T4, S2, S3, S4
                    ((w.tags["highway"] == "cycleway") and ("oneway" in w.tags) and (w.tags["oneway"] == "yes")) or
                    # T1, S3, S4
                    (("cycleway" in w.tags) and w.tags["cycleway"] == "track") or
                    # T2, T3
                    ((w.tags["highway"] == "cycleway") and ("oneway" in w.tags) and (w.tags["oneway"] == "no")) or
                    # T2, T3, T4
                    (("cycleway:right" in w.tags) and w.tags["cycleway:right"] == "track") or
                    (("cycleway:left" in w.tags) and w.tags["cycleway:left"] == "track") or
                    # S3, S5, S7
                    ((w.tags["highway"] in ["path", "footway", "cycleway"]) and ("bicycle" in w.tags) and (
                            w.tags["bicycle"] == "designated")) or
                    # B4, B5, B6
                    (("cycleway:right" in w.tags) and (
                            w.tags["cycleway:right"] == "share_busway")) or
                    (("cycleway:left" in w.tags) and (
                            w.tags["cycleway:left"] == "share_busway")) or
                    (("oneway:bicycle" in w.tags) and (w.tags["oneway:bicycle"] == "yes"))
            ):
                if oneway:
                    if ((w.tags["highway"] == "cycleway") and ("oneway" in w.tags) and (w.tags["oneway"] == "no")) or (
                            ("cycleway:right:oneway" in w.tags) and (w.tags["cycleway:right:oneway"] == "no")) or (
                            ("cycleway:left:oneway" in w.tags) and (w.tags["cycleway:left:oneway"] == "no")
                    ):
                        cycle_track_length = 2 * road_length
                    else:
                        cycle_track_length = road_length
                else:
                    cycle_track_length = road_length

            # Misc
            if (
                    # S6
                    (("ramp:bicycle" in w.tags) and (
                            w.tags["ramp:bicycle"] == "yes")) or
                    (("cyclestreet" in w.tags) and (w.tags["cyclestreet"] == "yes"))
            ):
                cycle_road_misc_length = road_length
                # Skip discounting oneways for misc, due to the difficult corner cases

            if self.decay_conf:
                road_length = self.apply_weight_decay(road_length, road_distance_from_centroid)
                cycle_lane_length = self.apply_weight_decay(cycle_lane_length, road_distance_from_centroid)
                cycle_track_length = self.apply_weight_decay(cycle_track_length, road_distance_from_centroid)
                cycle_road_misc_length = self.apply_weight_decay(cycle_road_misc_length, road_distance_from_centroid)

            self.total_road_length += road_length
            self.total_cycle_lane_length += cycle_lane_length
            self.total_cycle_track_length += cycle_track_length
            self.total_cycle_road_misc_length += cycle_road_misc_length
            self.total_cycling_road_length += cycle_lane_length + cycle_track_length + cycle_road_misc_length

    def way(self, w):
        self.parse_way_data(w)

    def node(self, n):
        if ("amenity" in n.tags) and n.tags["amenity"] == "bicycle_parking":
            self.parking_counter += 1
            # print(n.id)
            # raise ValueError


@stopwatch()
def main(osmfile, city_name, decay=False):
    with open(f"city_polygons/{city_name.lower()}.geojson") as f:
        city_json = json.load(f)

    city_polygon = shape(city_json)
    city_centroid = Point((city_polygon.centroid.y, city_polygon.centroid.x))

    if decay:
        with open(f"results/{city_name}_decay_conf.json", "r") as f:
            decay_conf = json.load(f)
    else:
        decay_conf = None

    handler = AmenityListHandler(city_centroid, decay_conf=decay_conf)
    handler.apply_file(osmfile, locations=True)

    # Multiply distances by 2 to count both ways
    summary = {
        "city_name": city_name,
        "total_road_length": (2 * handler.total_road_length) / 1000,
        "total_cycling_road_length": (2 * handler.total_cycling_road_length) / 1000,
        "total_cycle_lane_length": (2 * handler.total_cycle_lane_length) / 1000,
        "total_cycle_track_length": (2 * handler.total_cycle_track_length) / 1000,
        "total_cycle_road_misc_length": (2 * handler.total_cycle_road_misc_length) / 1000,
        "parking_counter": handler.parking_counter
    }

    print(summary)

    if decay:
        with open(f"results/{city_name}_decay.json", "w") as f:
            json.dump(summary, f)
    else:
        with open(f"results/{city_name}.json", "w") as f:
            json.dump(summary, f)

        with open(f"results/{city_name}_distances.pkl", "wb") as f:
            pickle.dump(handler.road_distances_from_centroid, f)

    return 0


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python %s <osmfile> <city_name>" % sys.argv[0])
        sys.exit(-1)

    osmfile = sys.argv[1]
    city_name = sys.argv[2]

    exit(main(osmfile, city_name, decay=False))
