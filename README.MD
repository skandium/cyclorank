`docker build osmium-caller .`

## Download full maps
`wget https://download.geofabrik.de/europe/netherlands-latest.osm.pbf`

## Extracting city polygons
`docker run -it -w /wkd -v $(pwd):/wkd osmium-caller:latest osmium getid -r -t full_maps/estonia-latest.osm.pbf r2164745 -o extracted_maps/tallinn_boundary.pbf --overwrite`
`docker run -it -w /wkd -v $(pwd):/wkd osmium-caller:latest osmium extract -p extracted_maps/tallinn_boundary.pbf full_maps/estonia-latest.osm.pbf -o extracted_maps/tallinn.pbf`

Use [Nomatim](https://nominatim.openstreetmap.org/ui/details.html?osmtype=R&osmid=2164745&class=boundary) to get the boundary IDs

## Run analytics
`python get_osmium_data.py extracted_maps/tallinn.pbf Tallinn`
`python download_and_extract_maps.py`
`python get_city_polygons.py`
`python run_map_analysis.py (without decay)`
`python get_decay_configs.py`
`python run_map_analysis.py (with decay)`