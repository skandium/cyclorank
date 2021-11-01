## Setup

`docker build -t osmium-caller .`
`city_conf.py` contains the metadata for cities

## Download full maps

`python download_and_extract_maps.py`

Use [Nomatim](https://nominatim.openstreetmap.org/ui/details.html?osmtype=R&osmid=2164745&class=boundary) to get the
boundary IDs

## Run analytics

`python get_city_polygons.py`
`python run_map_analysis.py (without decay)`
`python get_decay_configs.py`
`python run_map_analysis.py (with decay)`