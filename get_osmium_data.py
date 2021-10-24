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
        self.total_segregated_cycle_track_length = 0

        self.city_centroid = city_centroid
        self.road_distances_from_centroid = []

        self.parking_counter = 0

        self.decay_conf = decay_conf
        self.way_ids = []

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

    def parse_tag(self, w, tag, tag_values):
        if (tag in w.tags) and (w.tags[tag] in tag_values):
            return True
        else:
            return False

    # def parse_not_tag(self, w, tag, tag_values):
    #     if (tag in w.tags) and (w.tags[tag] not in tag_values):
    #         return True
    #     else:
    #         return False

    def parse_way_data(self, w):
        """Based on https://wiki.openstreetmap.org/wiki/Bicycle"""
        if "highway" in w.tags:
            # print(w.tags)
            # print(w.id)
            # print(w.nodes)
            # print(w.nodes[0].lat)
            # raise ValueError

            highway_length = o.geom.haversine_distance(w.nodes)
            first_node = w.nodes[0]
            road_distance_from_centroid = haversine(first_node.lat, first_node.lon, self.city_centroid.y,
                                                    self.city_centroid.x)
            self.road_distances_from_centroid.append(road_distance_from_centroid)

            cycle_lane_length = 0
            cycle_track_length = 0
            segregated_track_length = 0

            # Discount oneways
            if self.parse_tag(w, "oneway", ["yes"]):
                highway_length = 0.5 * highway_length

            # Cycle lanes
            if (
                    # L1a, L1b, M1, M2a, M2b, M2c, B2
                    (self.parse_tag(w, "cycleway", ["lane", "opposite_lane"])) or
                    # L1a, L1b, L2, M1, M2a, M2d, M3b, S2
                    (self.parse_tag(w, "cycleway:right", ["lane", "opposite_lane"])) or
                    # L1a, L1b, M1, M2b, M2d, M3a
                    (self.parse_tag(w, "cycleway:left", ["lane", "opposite_lane"])) or
                    # L1a
                    (self.parse_tag(w, "cycleway:both", ["lane", "opposite_lane"])) or
                    # B1
                    ("bicycle:lanes" in w.tags) or
                    # B3 / other share_busway values
                    (self.parse_tag(w, "cycleway",
                                    ["share_busway", "opposite_share_busway", "shoulder", "shared_lane"])) or
                    (self.parse_tag(w, "cycleway:right",
                                    ["share_busway", "opposite_share_busway", "shoulder", "shared_lane"])) or
                    (self.parse_tag(w, "cycleway:left",
                                    ["share_busway", "opposite_share_busway", "shoulder", "shared_lane"])) or
                    (self.parse_tag(w, "cycleway:both",
                                    ["share_busway", "opposite_share_busway", "shoulder", "shared_lane"])) or
                    # Sidewalks with explicit cycling
                    (self.parse_tag(w, "sidewalk:both:bicycle", ["designated", "yes"])) or
                    (self.parse_tag(w, "sidewalk:left:bicycle", ["designated", "yes"])) or
                    (self.parse_tag(w, "sidewalk:right:bicycle", ["designated", "yes"])) or
                    (self.parse_tag(w, "sidewalk:bicycle", ["designated", "yes"]))
            ):
                # Discount ways that do not have lane going both ways
                if not (
                        self.parse_tag(w, "cycleway", ["lane"]) or
                        self.parse_tag(w, "cycleway:both", ["lane"]) or
                        (self.parse_tag(w, "cycleway:right", ["lane"]) and self.parse_tag(w, "cycleway:left",
                                                                                          ["lane"])) or
                        (self.parse_tag(w, "cycleway:right", ["lane"]) and self.parse_tag(w, "cycleway:right:oneway",
                                                                                          ["no"])) or
                        (self.parse_tag(w, "cycleway:left", ["lane"]) and self.parse_tag(w, "cycleway:left:oneway",
                                                                                         ["no"]))
                ):
                    cycle_lane_length = highway_length * 0.5
                else:
                    cycle_lane_length = highway_length

            # Cycle tracks
            if (
                    (self.parse_tag(w, "cycleway", ["track", "opposite_track"])) or
                    (self.parse_tag(w, "cycleway:both", ["track", "opposite_track"])) or
                    (self.parse_tag(w, "cycleway:left", ["track", "opposite_track"])) or
                    (self.parse_tag(w, "cycleway:right", ["track", "opposite_track"])) or
                    (self.parse_tag(w, "highway", ["cycleway"])) or
                    (self.parse_tag(w, "highway", ["path", "footway"]) and self.parse_tag(w, "bicycle",
                                                                                          ["designated",
                                                                                           "yes"])) or
                    (self.parse_tag(w, "cyclestreet", ["yes"])) or
                    (self.parse_tag(w, "bicycle_road", ["yes"]))
                    # TODO What about this leftover from CyclOSM?
                    # (self.parse_not_tag(w, "sidewalk:both:bicycle", ["no"]) and self.parse_tag(w,
                    #                                                                            "sidewalk:left:segregated",
                    #                                                                            ["yes"])) or
                    # (self.parse_not_tag(w, "sidewalk:left:bicycle", ["no"]) and self.parse_tag(w,
                    #                                                                            "sidewalk:left:segregated",
                    #                                                                            ["yes"])) or
                    # (self.parse_not_tag(w, "sidewalk:right:bicycle", ["no"]) and self.parse_tag(w,
                    #                                                                            "sidewalk:right:segregated",
                    #                                                                            ["yes"]))
            ):
                # Discount oneways
                if (
                        (self.parse_tag(w, "highway", ["cycleway"]) and self.parse_tag(w, "oneway", ["yes"])) or
                        self.parse_tag(w, "oneway:bicycle", ["yes"]) or
                        self.parse_tag(w, "cycleway:right:oneway", ["yes"]) or
                        self.parse_tag(w, "cycleway:left:oneway", ["yes"])
                ):
                    cycle_track_length = 0.5 * highway_length
                else:
                    cycle_track_length = highway_length

                if self.parse_tag(w, "segregated", ["yes"]):
                    # print(w.id, w.tags)
                    segregated_track_length = cycle_track_length

            if self.decay_conf:
                highway_length = self.apply_weight_decay(highway_length, road_distance_from_centroid)
                cycle_lane_length = self.apply_weight_decay(cycle_lane_length, road_distance_from_centroid)
                cycle_track_length = self.apply_weight_decay(cycle_track_length, road_distance_from_centroid)

            if cycle_lane_length + cycle_track_length > 0:
                self.way_ids.append(w.id)

            self.total_road_length += highway_length
            self.total_cycle_lane_length += cycle_lane_length
            self.total_cycle_track_length += cycle_track_length
            self.total_segregated_cycle_track_length += segregated_track_length
            self.total_cycling_road_length += cycle_lane_length + cycle_track_length

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
        "total_segregated_cycle_track_length": (2 * handler.total_segregated_cycle_track_length) / 1000,
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

        with open(f"results/{city_name}_way_ids.pkl", "wb") as f:
            pickle.dump(handler.way_ids, f)

    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python %s <osmfile> <city_name>" % sys.argv[0])
        sys.exit(-1)

    osmfile = sys.argv[1]
    city_name = sys.argv[2]

    exit(main(osmfile, city_name, decay=False))
