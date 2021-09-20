"""
Extract all objects with an amenity tag from an osm file and list them
with their name and position.
This example shows how geometries from osmium objects can be imported
into shapely using the WKBFactory.
"""
import osmium as o
import sys
import json

from geoflow.utils import stopwatch


class AmenityListHandler(o.SimpleHandler):
    def __init__(self):
        super(AmenityListHandler, self).__init__()
        self.total_road_length = 0
        self.total_cycling_road_length = 0
        self.total_cycle_lane_length = 0
        self.total_cycle_track_length = 0

    def parse_way_data(self, w):
        """Based on https://wiki.openstreetmap.org/wiki/Bicycle"""
        if 'highway' in w.tags:
            # # if "cycleway:right" in w.tags:
            # #     print(w.id)
            # #     raise ValueError
            # #
            # # Cycling lanes
            # if ("cycleway" in w.tags):
            #     if w.tags["cycleway"] == "lane":
            #     lane_length = o.geom.haversine_distance(w.nodes)
            # elif (("cycleway:left" in w.tags) and ("cycleway:right" in w.tags)) or ("cycleway:both" in w.tags):
            #     lane_length = o.geom.haversine_distance(w.nodes)
            # elif
            # TODO parse road length with discounting

            self.total_road_length += o.geom.haversine_distance(w.nodes)
            if ("cycleway" in w.tags) or (w.tags["highway"] == "cycleway") or ("bicycle" in w.tags) or (
                    "oneway:bicycle" in w.tags) or ("bicycle:backward" in w.tags) or ("cyclestreet" in w.tags):
                # try:
                self.total_cycling_road_length += o.geom.haversine_distance(w.nodes)
                # except o.InvalidLocationError:
                #     # A location error might occur if the osm file is an extract
                #     # where nodes of ways near the boundary are missing.
                #     print("WARNING: way %d incomplete. Ignoring." % w.id)

    def way(self, w):
        self.parse_way_data(w)


@stopwatch()
def main(osmfile, city_name):
    handler = AmenityListHandler()
    handler.apply_file(osmfile, locations=True)

    summary = {
        "city_name": city_name,
        "total_road_length": handler.total_road_length / 1000,
        "total_cycling_road_length": handler.total_cycling_road_length / 1000
    }

    print(summary)
    with open(f"results/{city_name}.json", "w") as f:
        json.dump(summary, f)

    return 0


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python %s <osmfile>" % sys.argv[0])
        sys.exit(-1)

    osmfile = sys.argv[1]
    city_name = sys.argv[2]

    exit(main(osmfile, city_name))
