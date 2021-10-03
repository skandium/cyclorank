import json
import requests
import os
import time
from city_conf import city_mappings

for country_map in city_mappings:
    for city in city_mappings[country_map]:
        city_name = list(city.keys())[0]
        print(f"Getting polygon for {city_name}")
        try:
            if "centre" not in city:
                if not os.path.exists(f"city_polygons/{city_name.lower()}.geojson"):
                    print("Downloading")
                    city_osm_id = city[city_name]["osm_id"]
                    r = requests.get(f"http://polygons.openstreetmap.fr/get_geojson.py?id={city_osm_id}&params=0")
                    city_polygon = r.json()
                    with open(f"city_polygons/{city_name.lower()}.geojson", "w") as f:
                        json.dump(city_polygon, f)
                    time.sleep(3)
                else:
                    print("Exists - skipping")
            else:
                print("Centre exists - skipping")
        except Exception as e:
            print(f"Error: {e}")
