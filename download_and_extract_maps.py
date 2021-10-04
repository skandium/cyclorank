import subprocess
import os
from city_conf import city_mappings as country_to_cities

GEOFABRIK_ROOT_PATH = "https://download.geofabrik.de/"


def download_map(geofabrik_path):
    full_path = GEOFABRIK_ROOT_PATH + geofabrik_path
    subprocess.run(["wget", "-P", "full_maps", full_path])
    filename = geofabrik_path.split("/")[-1]
    return filename


def extract_map(city_name, relation_id, full_map_path):
    print(f"Working on map for {city_name} - id {relation_id}")
    print("Extracting boundary")
    subprocess.run(
        f"docker run -it -w /wkd -v $(pwd):/wkd osmium-caller:latest osmium getid -r -t full_maps/{full_map_path} r{relation_id} -o extracted_maps/{city_name}_boundary.pbf",
        shell=True)
    print("Extracting city")
    subprocess.run(
        f"docker run -it -w /wkd -v $(pwd):/wkd osmium-caller:latest osmium extract -p extracted_maps/{city_name}_boundary.pbf full_maps/{full_map_path} -o extracted_maps/{city_name}.pbf",
        shell=True)

    if os.path.exists(f"extracted_maps/{city_name}.pbf"):
        print("Removing boundary file")
        subprocess.run(f"rm extracted_maps/{city_name}_boundary.pbf", shell=True)


if __name__ == "__main__":
    for country_map in country_to_cities:
        try:
            missing_cities = []
            for city in country_to_cities[country_map]:
                city_name = list(city.keys())[0]

                if not os.path.exists(f"extracted_maps/{city_name}.pbf"):
                    missing_cities.append(city)

            if missing_cities:
                print(f"Map: {country_map}")
                print(f"Missing cities: {missing_cities}")
                full_map_path = download_map(country_map)
                # full_map_path = "greece-latest.osm.pbf"

                for missing_city in missing_cities:
                    for missing_city_name in missing_city:
                        osm_id = missing_city[missing_city_name]["osm_id"]
                        extract_map(missing_city_name, osm_id, full_map_path=full_map_path)

                # print("Removing country map")
                # subprocess.run(f"rm full_maps/{full_map_path}", shell=True)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(e)
            continue
