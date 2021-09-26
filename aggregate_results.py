import json
import pandas as pd

from city_conf import cities

from shapely.geometry import Point, shape
from geoflow.utils import stopwatch
from geoflow.spatial import haversine
import pyproj
import shapely
import shapely.ops as ops
from shapely.geometry.polygon import Polygon
from functools import partial


def find_polygon_area(geojson):
    geom = shape(geojson)
    geom_area = ops.transform(
        partial(
            pyproj.transform,
            pyproj.Proj(init='EPSG:4326'),
            pyproj.Proj(
                proj='aea',
                lat_1=geom.bounds[1],
                lat_2=geom.bounds[3]
            )
        ),
        geom)
    return geom_area.area / 1e6


city_records = []
for city_name in cities:
    try:
        with open(f"results/{city_name}.json", "r") as f:
            city_record = json.load(f)

        with open(f"city_polygons/{city_name.lower()}.geojson") as f:
            city_geojson = json.load(f)

        city_record["area_km2"] = find_polygon_area(city_geojson)
        city_records.append(city_record)
    except:
        continue

df = pd.DataFrame(city_records)

city_records_with_decay = []
for city_name in cities:
    try:
        with open(f"results/{city_name}_decay.json", "r") as f:
            city_record = json.load(f)

        with open(f"city_polygons/{city_name.lower()}.geojson") as f:
            city_geojson = json.load(f)

        city_record["area_km2"] = find_polygon_area(city_geojson)
        city_records_with_decay.append(city_record)
    except:
        continue

df_decay = pd.DataFrame(city_records_with_decay)

df["cycle_road_share"] = df["total_cycling_road_length"] / df["total_road_length"]
df_decay["cycle_road_share"] = df_decay["total_cycling_road_length"] / df_decay["total_road_length"]

df["cycle_track_share"] = df["total_cycle_track_length"] / df["total_road_length"]
df_decay["cycle_track_share"] = df_decay["total_cycle_track_length"] / df_decay["total_road_length"]

df.sort_values("cycle_road_share")
df_decay.sort_values("cycle_road_share")

df.sort_values("cycle_track_share")
df_decay.sort_values("cycle_track_share")

# df_decay["parking_per_km2"] = df_decay["parking_counter"] / df_decay["area_km2"]

# Ranking

df["rank_cycle_road_share"] = df["cycle_road_share"].rank(ascending=False).astype(int)
df["rank_cycle_track_share"] = df["cycle_track_share"].rank(ascending=False).astype(int)

df_decay["rank_cycle_road_share"] = df_decay["cycle_road_share"].rank(ascending=False).astype(int)
df_decay["rank_cycle_track_share"] = df_decay["cycle_track_share"].rank(ascending=False).astype(int)

merged = df.merge(df_decay, on="city_name", suffixes=["", "_decayed"])

merged["overall_score"] = merged["cycle_road_share"] * merged["cycle_track_share"] * merged[
    "cycle_road_share_decayed"] * merged["cycle_track_share_decayed"]
merged["overall_rank"] = merged["overall_score"].rank(ascending=False).astype(int)

final = merged[
    ["city_name", "area_km2", "total_road_length", "cycle_road_share", "cycle_track_share", "rank_cycle_road_share",
     "rank_cycle_track_share", "rank_cycle_road_share_decayed", "rank_cycle_track_share_decayed", "overall_rank"]]

final.sort_values("overall_rank").to_csv("final_results.csv", index=False)
