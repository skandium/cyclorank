import subprocess
from shutil import copyfile

from city_conf import cities


def prepare_maps(city_name):
    copyfile(f"extracted_maps/{city_name}.pbf", f"map_car/{city_name}.pbf")
    copyfile(f"extracted_maps/{city_name}.pbf", f"map_bike/{city_name}.pbf")
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
    for city_name in cities:
        try:
            prepare_maps(city_name)
        except KeyboardInterrupt:
            raise
        except:
            continue
