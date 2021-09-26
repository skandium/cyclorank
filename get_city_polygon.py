import json
import requests
import time
from city_conf import cities

for city_name in cities:
    print(city_name)

    try:
        city_osm_id = cities[city_name]["osm_id"]
        r = requests.get(f"http://polygons.openstreetmap.fr/get_geojson.py?id={city_osm_id}&params=0")
        city_polygon = r.json()

        with open(f"city_polygons/{city_name.lower()}.geojson", "w") as f:
            json.dump(city_polygon, f)
    except Exception as e:
        print(f"Error: {e}")

    time.sleep(3)
