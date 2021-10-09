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
            # Get city polygon
            if not os.path.exists(f"city_polygons/{city_name.lower()}_polygon.geojson"):
                city_osm_id = city[city_name]["osm_id"]
                r = requests.get(f"http://polygons.openstreetmap.fr/get_geojson.py?id={city_osm_id}&params=0")
                city_geojson = r.json()
                time.sleep(3)  # Have mercy on endpoint

                with open(f"city_polygons/{city_name.lower()}_polygon.geojson", "w") as f:
                    json.dump(city_geojson, f)
            else:
                print("Exists - skipping")

            # Save centre coordinates
            centre_coordinates = city[city_name]["centre"]
            city_centre = {
                "type": "GeometryCollection",
                "geometries": [
                    {"type": "Point",
                     "coordinates": [centre_coordinates[0], centre_coordinates[1]]}]}

            with open(f"city_polygons/{city_name.lower()}.geojson", "w") as f:
                json.dump(city_centre, f)

        except Exception as e:
            print(f"Error: {e}")
