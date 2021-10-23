import requests
from tqdm import tqdm
import pickle
import json

host_port = {
    "car": 5000,
    "bike": 5001
}


def call_osrm_route(start_point, end_point, vehicle_type):
    host = f"http://localhost:{host_port[vehicle_type]}"

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

    return {"distance": first_route["distance"], "duration": first_route["duration"]}


if __name__ == "__main__":
    city_name = "Amsterdam"
    vehicle_type = "car"

    with open(f"routes/{city_name.lower()}.p", "rb") as f:
        routes = pickle.load(f)

    results = []
    for route in tqdm(routes):
        route = call_osrm_route((route[0], route[1]), (route[2], route[3]), vehicle_type=vehicle_type)
        results.append(route)

    with open(f"routing_results/{city_name}_{vehicle_type}.json", "w") as f:
        json.dump(results, f)
