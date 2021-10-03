import numpy as np
import pickle
import json
import matplotlib.pyplot as plt

from city_conf import cities

WEIGHT_AT_UPPER_THRESHOLD = 0.1


def derive_exponential_decay_params(dists):
    """Calibrate decay to put weight 0.1 at 90th percentile of road distance from centroid,
    and 1.0 at 10th percentile"""
    lower_threshold = np.percentile(dists, 10)
    upper_threshold = np.minimum(np.percentile(dists, 90), 15)
    decay_coef = np.log(WEIGHT_AT_UPPER_THRESHOLD) / (upper_threshold - lower_threshold)

    return {
        "lower_threshold": round(lower_threshold, 1),
        "upper_threshold": round(upper_threshold, 1),
        "decay_coef": round(decay_coef, 2)
    }


for city_name in cities:
    print(city_name)
    with open(f"results/{city_name}_distances.pkl", "rb") as f:
        dists = pickle.load(f)

    decay_conf = derive_exponential_decay_params(dists)
    with open(f"results/{city_name}_decay_conf.json", "w") as f:
        json.dump(decay_conf, f)

    plt.hist(dists, bins=100)
    plt.axvline(x=decay_conf["lower_threshold"], color="red")
    plt.axvline(x=decay_conf["upper_threshold"], color="red")
    plt.title(city_name)
    plt.savefig(f"results/{city_name}_distance_plot.png")
    plt.close()
