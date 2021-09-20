import subprocess
import os
from city_conf import cities

GEOFABRIK_ROOT_PATH = "https://download.geofabrik.de/"


def download_map(geofabrik_path):
    full_path = GEOFABRIK_ROOT_PATH + geofabrik_path
    subprocess.run(["wget", "-P", "full_maps", full_path])
    filename = geofabrik_path.split("/")[-1]
    return filename


def extract_map(city_name, relation_id, full_map_path):
    print("Extracting boundary")
    subprocess.run(
        f"docker run -it -w /wkd -v $(pwd):/wkd osmium-caller:latest osmium getid -r -t full_maps/{full_map_path} r{relation_id} -o extracted_maps/{city_name}_boundary.pbf",
        shell=True)
    print("Extracting city")
    subprocess.run(
        f"docker run -it -w /wkd -v $(pwd):/wkd osmium-caller:latest osmium extract -p extracted_maps/{city_name}_boundary.pbf full_maps/{full_map_path} -o extracted_maps/{city_name}.pbf",
        shell=True)

    print("Removing intermediate files")
    subprocess.run(f"rm full_maps/{full_map_path}", shell=True)
    subprocess.run(f"rm extracted_maps/{city_name}_boundary.pbf", shell=True)


if __name__ == "__main__":
    # cities = {"Nicosia": {
    #     "geofabrik_path": "europe/cyprus-latest.osm.pbf",
    #     "osm_id": 2628521
    # }}

    for i, city_name in enumerate(cities):
        try:
            if os.path.exists(f"extracted_maps/{city_name}.pbf"):
                print(f"Skipping {city_name} as it exists already")
                continue

            print(f"Extracting map for {city_name}")
            full_map_path = download_map(cities[city_name]["geofabrik_path"])
            if cities[city_name]["osm_id"]:
                extract_map(city_name, cities[city_name]["osm_id"], full_map_path)
        except KeyboardInterrupt:
            raise
        except:
            continue
