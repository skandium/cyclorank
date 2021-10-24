import subprocess
import time
import os
import requests
from tqdm import tqdm
import pickle
import json


# host_port = {
#     "car": 5000,
#     "bike": 5001
# }


def host_osrm(city_name, vehicle_type):
    # port = host_port[vehicle_type]

    # subprocess.Popen(
    #     f"docker run -t -i -p {port}:{port} -v {f'map_{vehicle_type}'}:/data osrm/osrm-backend osrm-routed --algorithm mld --port {port} /data/{city_name}.osrm")
    print(f"Opening router for {vehicle_type}")
    command = f"docker run -t -i -p 5000:5000 -v {f'{os.getcwd()}/map_{vehicle_type}'}:/data osrm/osrm-backend osrm-routed --algorithm mld /data/{city_name}.osrm"
    print(command)
    process = subprocess.Popen(command, shell=True)
    time.sleep(5)
    return process


def call_osrm_route(start_point, end_point, vehicle_type):
    # host = f"http://localhost:{host_port[vehicle_type]}"
    host = "http://localhost:5000"

    start_lat, start_lng = start_point
    end_lat, end_lng = end_point

    query = host + f"/route/v1/driving/{start_lng},{start_lat};{end_lng},{end_lat}?steps=false&alternatives=false"
    r = requests.get(query).json()
    try:
        first_route = r["routes"][0]
    except KeyError:  # NoRoute?
        first_route = {
            "distance": -1,
            "duration": -1
        }

    return {
        "start_lat": start_lat,
        "start_lng": start_lng,
        "end_lat": end_lat,
        "end_lng": end_lng,
        "distance": first_route["distance"],
        "duration": first_route["duration"]}


if __name__ == "__main__":
    for city_name in ["Bucharest"]:
        # city_name = "Tallinn"
        for vehicle_type in ["car", "bike"]:
            process = host_osrm(city_name, vehicle_type)

            with open(f"routes/{city_name.lower()}.p", "rb") as f:
                routes = pickle.load(f)

            results = []
            # for route in tqdm(routes):
            for route in routes:
                route = call_osrm_route((route[0], route[1]), (route[2], route[3]), vehicle_type=vehicle_type)
                results.append(route)

            with open(f"routing_results/{city_name}_{vehicle_type}.json", "w") as f:
                json.dump(results, f)

            process.terminate()
