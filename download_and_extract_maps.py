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

    print("Removing boundary file")
    if os.path.exists(f"extracted_maps/{city_name}.pbf"):
        subprocess.run(f"rm extracted_maps/{city_name}_boundary.pbf", shell=True)


if __name__ == "__main__":
    # cities = {"Nicosia": {
    #     "geofabrik_path": "europe/cyprus-latest.osm.pbf",
    #     "osm_id": 2628521
    # }}

    # for i, city_name in enumerate(cities):
    #     try:
    #         if os.path.exists(f"extracted_maps/{city_name}.pbf"):
    #             print(f"Skipping {city_name} as it exists already")
    #             continue
    #
    #         print(f"Extracting map for {city_name}")
    #         full_map_path = download_map(cities[city_name]["geofabrik_path"])
    #         if cities[city_name]["osm_id"]:
    #             extract_map(city_name, cities[city_name]["osm_id"], full_map_path)
    #     except KeyboardInterrupt:
    #         raise
    #     except:
    #         continue

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

                for missing_city in missing_cities:
                    for missing_city_name in missing_city:
                        osm_id = missing_city[missing_city_name]["osm_id"]
                        extract_map(missing_city_name, osm_id, full_map_path=full_map_path)

                print("Removing country map")
                subprocess.run(f"rm full_maps/{full_map_path}", shell=True)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(e)
            continue

            # print(missing_city_name, osm_id)
            # print("Extracting ")
            # osm_id = list(miss)
            # extract_map(missing_city_name, cities[city_name]["osm_id"], full_map_path)
            #         print(f"Skipping {city_name} as it exists already")

            # print(f"Extracting map for {city_name}")
            # full_map_path = download_map(cities[city_name]["geofabrik_path"])
            # if cities[city_name]["osm_id"]:
            #     extract_map(city_name, cities[city_name]["osm_id"], full_map_path)
