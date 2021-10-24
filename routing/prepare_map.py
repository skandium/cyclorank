import subprocess
from shutil import copyfile

# from city_conf import city_mappings


def prepare_maps(city_name):
    copyfile(f"../extracted_maps/{city_name}.pbf", f"map_car/{city_name}.pbf")
    copyfile(f"../extracted_maps/{city_name}.pbf", f"map_bike/{city_name}.pbf")
    print("Preparing car map")
    subprocess.run(
        f"docker run -t -v $(pwd):/data osrm/osrm-backend osrm-extract -p /opt/car.lua /data/map_car/{city_name}.pbf",
        shell=True)

    subprocess.run(
        f"docker run -t -v $(pwd):/data osrm/osrm-backend osrm-partition /data/map_car/{city_name}.pbf",
        shell=True)

    subprocess.run(
        f"docker run -t -v $(pwd):/data osrm/osrm-backend osrm-customize /data/map_car/{city_name}.pbf",
        shell=True)

    print("Preparing bike map")
    subprocess.run(
        f"docker run -t -v $(pwd):/data osrm/osrm-backend osrm-extract -p /opt/bicycle.lua /data/map_bike/{city_name}.pbf",
        shell=True)

    subprocess.run(
        f"docker run -t -v $(pwd):/data osrm/osrm-backend osrm-partition /data/map_bike/{city_name}.pbf",
        shell=True)

    subprocess.run(
        f"docker run -t -v $(pwd):/data osrm/osrm-backend osrm-customize /data/map_bike/{city_name}.pbf",
        shell=True)


if __name__ == "__main__":
    # city_mappings = {
    # 'europe/austria-latest.osm.pbf': [{'Vienna': {'osm_id': 109166, 'centre': (48.2083537, 16.3725042)}}],
    # 'europe/belgium-latest.osm.pbf': [{'Brussels': {'osm_id': 2404020, 'centre': (50.83879505, 4.375304132256188)}},
    #                                   {'Antwerp': {'osm_id': 59518, 'centre': (51.2602708, 4.382181448976495)}}],
    # 'europe/bulgaria-latest.osm.pbf': [{'Sofia': {'osm_id': 4283101, 'centre': (42.6978634, 23.3221789)}},
    #                                    {'Plovdiv': {'osm_id': 1955801, 'centre': (42.14390815, 24.742123302454544)}},
    #                                    {'Varna': {'osm_id': 1437135, 'centre': (43.21324335, 27.61943526469872)}}],
    # 'europe/croatia-latest.osm.pbf': [{'Zagreb': {'osm_id': 3168167, 'centre': (45.8131847, 15.9771774)}}],
    # 'europe/cyprus-latest.osm.pbf': [{'Nicosia': {'osm_id': 2628521, 'centre': (35.1739302, 33.364726)}}]
    # }
    #
    # for country_map in city_mappings:
    #     for city in city_mappings[country_map]:
    #         city_name = list(city.keys())[0]
    #         try:
    #             # map_path = f"extracted_maps/{city_name.lower()}.pbf"
    #             # results_path = f"results/{city_name}_decay.json"
    #             # if os.path.exists(results_path):
    #             #     print(f"Skipping {city_name}")
    #             # else:
    #             #     print(f"Working on {city_name}")
    #             #     main(map_path, city_name, decay=True)
    #         # except KeyboardInterrupt:
    #         #     raise
    #         # except Exception as e:
    #         #     print(e)
    #         #     continue

    # cities = ["Tallinn", "Helsinki", ""]
    cities = ["Bucharest"]
    for city_name in cities:
        try:
            prepare_maps(city_name)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(e)
            continue
