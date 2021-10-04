from city_conf import city_mappings
import os
from get_osmium_data import main

if __name__ == "__main__":
    for country_map in city_mappings:
        for city in city_mappings[country_map]:
            city_name = list(city.keys())[0]
            try:
                map_path = f"extracted_maps/{city_name.lower()}.pbf"
                results_path = f"results/{city_name}.json"
                # if os.path.exists(results_path):
                #     print(f"Skipping {city_name}")
                # else:
                print(f"Working on {city_name}")
                main(map_path, city_name, decay=True)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(e)
                continue
