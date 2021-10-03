from city_conf import cities
from get_osmium_data import main

if __name__ == "__main__":
    for i, city_name in enumerate(cities):
        try:
            print(f"City {city_name}")
            map_path = f"extracted_maps/{city_name.lower()}.pbf"
            main(map_path, city_name, decay=False)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(e)
            continue
