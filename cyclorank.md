# CycloRank

I measure and rank the cycling infrastructure of European cities by using crowdsourced data from OpenStreetMap. The
cities included have either a population above 400K people, or are EU capitals.

## Motivation

I've been adhering this year to a personal challenge to cycle as my main mode of inner city transport. This coincided
with a period of massive resurgence in cycling popularity across Europe, as cities
like [Paris](https://www.euronews.com/green/2021/10/25/paris-is-investing-250-million-to-become-a-100-cycling-city)
or [Berlin](https://momentummag.com/berlin-unveils-3000-kilometer-cycling-network/)
have made significant investments to boost the modal share of cycling after the lockdowns. Even in my home city of
Tallinn, where supposedly only [1%](https://transpordiamet.ee/media/526/download) of trips are by bike, it became a
dominant topic in this year's local election. As in any politicised debate there is a tendency to revert from facts to
suitable narratives, I started wondering if there's an objective view based on data that would help to evaluate and rank
the efforts of different cities in making their environments more bike friendly. After all, every city probably looks up
to Copenhagen or Amsterdam in this respect, but how well are the others doing?
[OpenStreetMap](https://en.wikipedia.org/wiki/OpenStreetMap), the world's largest open source geographic database might
provide some of these answers.

## Similar projects

There already are a few similar rankings that I could find. For example,
the [Copenhagenize Index](https://copenhagenizeindex.eu/) gives subjective scores to on a variety of areas such as
streetscape, culture and ambition. The city list comprises of 600 cities with 600 000 inhabitants worldwide. Another one
is the [Bicycle Cities Index](https://www.coya.com/bike/index-2019) by digital insurance company Coya. The city list
selection is subjective, however the measurement is done on a number of objective indicators sourced across the
internet, such as road infrastructure, bicycle usage, number of fatalities etc.

The reasons for developing yet another one:

* Copenhagenize Index and Bicycle Cities Index were last updated in 2019
* We want to treat fairly both the city selection (based on population size) and the metric measurement, refraining from
  subjective expert-assigned scores or manual lookup of data from different sources
* Using a standardised methodology based on OpenStreetMap will allow to repeat the experiment at a different time and
  scale it to an arbitrary number of cities, with little manual additional effort

## Methodology

To measure the cyclability of cities, I calculate the share of road infrastructure that has been marked explicitly as
cycling friendly (either a bike lane or bike road) on [OpenStreetMap](https://wiki.openstreetmap.org/wiki/Bicycle). The
entire navigable length is considered, thus a oneway road has half the length of a twoway.

The motivation behind measuring cycling path length is twofold: firstly, it has been shown to correlated to the
popularity of cycling [\[1\]](https://www.sciencedirect.com/science/article/pii/S2214140519301033) and secondly, the
presence of dedicated bike lanes is correlated with increased safety, which should have a further reinforcement effect
on cycling popularity. While building many cycling lanes alone is not enough to facilitate a transition to widespread
cycling, it is probably a necessary condition.

To qualify as a cycling road, an OpenStreetMap [way](https://wiki.openstreetmap.org/wiki/Way) has to either:

* have lanes dedicated to cyclists or shared with buses (counted as lanes)
* have a sidewalk that explicitly allows cycling (counted as lanes)
* be a separate track for cyclists, a cycle street (mostly Belgium/Netherlands) or a bicycle road (mostly Germany)
* be a path or footway that has been designated to cyclists
  by [signs](https://wiki.openstreetmap.org/wiki/Tag:bicycle%3Ddesignated#:~:text=bicycle%20%3D%20designated%20is%20applied%20where,as%20cycleway%3Aboth%20%3D%20lane%20.)

It is worth noting that this definition of cycling road is far more restrictive than what a router such
as [OSRM](https://map.project-osrm.org/?z=14&center=59.439599%2C24.770308&loc=58.669798%2C24.079285&hl=en&alt=0&srv=1)
or Google Maps would use. That's because for high connectivity and actually calculating sensible routes between any
points A and B, routers often guide through ordinary, potentially unsafe streets. As a matter of fact, the part of the
road network considered in this study is only roughly 10% of all considered cyclable in OSRM.

### Additional metrics

While the main ranking is based on the above, I also calculate a few auxiliary metrics:

* Share of segregated cycling tracks. This is the golden standard of  
  Blablabla

### Spatial weighting

A possible caveat of the above approach is the topology of the city. Theoretically, a city could build many recreational
bike roads near the outskirts of the city, where space is abundant, but develop nothing in the city centre. This would
not faciliate cycling for commuting. For this reason, I apply exponential decay weights to the road lengths, where the
weights are a function of the road's distance from the city centre. More precisely, the formula for weighting is:

`exp(decay_coef * min(max(distance - t_min), t_max))`

where the t_min = 10th percentile of road distances from centre and t_max = max(90th percentile of the same, 15km). This
guarantees two things:

* A road in the city centre has 10 times higher weight than a road on the 90th percentile of distance from city centre
* Censoring t_max at 15km makes sure we do not put weight to far away roads, in case the city polygon is very large

This is visualised below on the example of Tallinn, where the circle around the centroid with radius 8km (the 90th
percentile) denotes the distance at which a road has 10 times less weight than a road in the city centre.

![circle](imgs/circle.png)

### Software used

OpenStreetMap Osmium Pyrosm Nomatim French site

## Results

Below are the ranking by cycling road share, with additional information such as the city polygon area,

### TOP 20

### Overall

## Discussion

To see whether the ranking is capturing the intended semantic concepts, it is useful to visualise the cycling
infrastructure on a map and compare it to our quantitative measurements. I
use [CyclOSM](https://www.cyclosm.org/#map=12/47.1842/-1.5288/cyclosm), which should be the best such tool.

Firstly, comparing a top ranking city with a bottom one shows that indeed, the overall level of infrastructure is
captured:

### Copenhagen vs Sofia

### Nantes vs Barcelona

Nantes is an interesting outlier - it has the most bike road share out of any city, but is only 15th in the ranking by
separated cycle tracks. Indeed, it visibly has predominently cycling lanes (marked by the dashed line), rather than
separate cycleways.

Contrasting this is Barcelona - anyone who's cycled there knows the convenience of their designated cycleways that have
little overlap with car traffic. Indeed, this is apparent visually.
