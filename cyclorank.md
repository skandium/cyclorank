# CycloRank

## Motivation

I live in Tallinn, a cosy northern EU capital known for its innovative digital solutions. I like to cycle both for
recreation and commuting. While Tallinn may be no Copenhagen in terms of cycling safety and convenience, I've often
wondered how does it fare compared to other European cities. I decided to try to use some of today's novel digital tools
to quantify how competitive different European capitals are in terms of their biking infrastructure.

## Methodology

### City selection

It is therefore a quasi-EU ranking, meaning that for the cities to be included, they needed to be either:

* Above 400K population from EU/Norway/Switzerland/UK
* An EU capital

### Similar projects

Other similar cyclability rankings include the [Copenhagenize Index](https://copenhagenizeindex.eu/) which gives
subjective scores to on a variety of areas such as streetscape, culture and ambition. The city list comprises of 600
cities with 600 000 inhabitants worldwide. Another similar project is
the [Bicycle Cities Index](https://www.coya.com/bike/index-2019) by digital insurance company Coya. The city list
selection is subjective, however the measurement is done on a number of objective indicators sourced across the
internet, such as road infrastructure, bicycle usage, number of fatalities etc.

There are a few reasons for developing yet another ranking:

* Copenhagenize Index and Bicycle Cities Index were last updated in 2019
* We want to treat objectively both the city selection (based on population size) and the metric measurement, refraining
  from subjective expert-assigned scores or manual lookup of data from different sources
* Using a standardised methodology based on OpenStreetMap will allow to repeat the experiment at a different time and
  scale it to an arbitrary number of cities

### Metric definitions

Therefore, to measure the cyclability of cities, I look at the share of road infrastructure that has been marked
explicitly as cycling friendly (either a bike lane or bike road)
on [OpenStreetMap](https://wiki.openstreetmap.org/wiki/Bicycle). As designated bike roads can be considered
qualitatively better, I also calculate their separate share.

The motivation behind measuring cycling path length is twofold: firstly, it has been shown to correlated to the
popularity of cycling [\[1\]](https://www.sciencedirect.com/science/article/pii/S2214140519301033) and secondly, the
presence of dedicated bike lanes is correlated with increased safety, which should have a further reinforcement effect
on cycling popularity. While building cycling lanes alone is not enough to facilitate a transition to widespread
cycling, it is probably a necessary condition.

A possible caveat of the above approach is the topology of the city. Theoretically, a city could build many recreational
bike roads near the outskirts of the city, where space is abundant, but develop nothing in the city centre. This would
not faciliate cycling for commuting. For this reason, I also calculate a proxy to *useful* bike path length, which is
defined as the weighted sum of bike path lengths, where exponential decay weights are applied to bike lanes as a
function of their distance from the city centre. More precisely, the formula for weighting is:

where the t_min = 10th percentile of road distances from centre and t_max = max(90th percentile of the same, 15km). This
guarantees two things:

* A road in the city centre has 10 times higher weight than a road on the 90th percentile of distance from city centre
* Censoring t_max at 15km makes sure we do not put weight to far away roads, in case the city polygon is very large

The final ranking will be a geometric average of 4 measurements:

* share of cycling roads
* share of cycling tracks
* share of cycling roads (weighted)
* share of cycling tracks (weighted)

## Results

### TOP 20

### Comparison with other indices

### Overall

| city_name  | area_km2 | total_road_length | cycle_road_share | cycle_track_share | rank_cycle_road_share | rank_cycle_track_share | rank_cycle_road_share_decayed | rank_cycle_track_share_decayed | overall_rank |
|------------|----------|-------------------|------------------|-------------------|-----------------------|------------------------|-------------------------------|--------------------------------|--------------|
| Copenhagen |  108.951 |          2503.605 |            0.185 |             0.172 |                     1 |                      3 |                             1 |                              1 |            1 |
| Amsterdam  |  219.504 |          5053.707 |            0.178 |             0.167 |                     4 |                      4 |                             2 |                              2 |            2 |
| Stockholm  |  215.754 |          5617.459 |            0.183 |             0.176 |                     2 |                      1 |                             4 |                              3 |            3 |
| Helsinki   |  717.645 |          7514.957 |            0.179 |             0.175 |                     3 |                      2 |                             6 |                              4 |            4 |
| Paris      |  105.391 |          3849.004 |            0.154 |              0.11 |                     5 |                      5 |                             3 |                              5 |            5 |
| Brussels   |   12.839 |           537.147 |            0.153 |             0.089 |                     6 |                      6 |                             5 |                              6 |            6 |
| Berlin     |  891.144 |         20956.899 |            0.094 |             0.075 |                     7 |                      8 |                             8 |                              8 |            7 |
| Vienna     |  414.863 |          9084.371 |             0.09 |             0.066 |                     8 |                      9 |                             7 |                              9 |            8 |
| Tallinn    |  159.463 |          3511.257 |            0.084 |             0.075 |                     9 |                      7 |                            10 |                             10 |            9 |
| Ljubljana  |   275.06 |          3475.257 |            0.069 |             0.057 |                    10 |                     10 |                             9 |                              7 |           10 |
| Luxembourg |   51.731 |          1217.451 |            0.069 |             0.055 |                    11 |                     11 |                            11 |                             11 |           11 |
| Lisbon     |   86.819 |          2693.282 |            0.047 |             0.046 |                    14 |                     13 |                            13 |                             12 |           12 |
| Warsaw     |   517.27 |         14414.383 |            0.049 |             0.047 |                    13 |                     12 |                            14 |                             13 |           13 |
| Vilnius    |  393.747 |          5786.613 |            0.035 |             0.034 |                    16 |                     15 |                            15 |                             14 |           14 |
| Dublin     |  118.622 |          3137.746 |            0.056 |             0.025 |                    12 |                     17 |                            12 |                             19 |           15 |
| Zagreb     |  308.789 |          5090.867 |            0.037 |             0.036 |                    15 |                     14 |                            17 |                             15 |           16 |
| Budapest   |  526.146 |          9968.712 |            0.033 |             0.024 |                    17 |                     18 |                            16 |                             16 |           17 |
| Madrid     |  604.892 |         11564.277 |             0.03 |             0.027 |                    18 |                     16 |                            22 |                             21 |           18 |
| Bratislava |  367.559 |           5816.31 |            0.024 |             0.021 |                    19 |                     19 |                            21 |                             20 |           19 |
| Rome       | 1286.583 |         12734.446 |             0.02 |             0.019 |                    20 |                     20 |                            20 |                             17 |           20 |
| Riga       |  304.009 |          5531.033 |             0.02 |             0.018 |                    21 |                     21 |                            19 |                             18 |           21 |
| Sofia      |  177.003 |          3648.689 |             0.02 |             0.014 |                    22 |                     23 |                            18 |                             22 |           22 |
| Nicosia    |   20.526 |           360.478 |            0.014 |             0.014 |                    23 |                     22 |                            24 |                             24 |           23 |
| Bucharest  |  240.377 |          4584.483 |            0.008 |             0.007 |                    24 |                     24 |                            23 |                             23 |           24 |
| Valletta   |     0.84 |            33.853 |                0 |                 0 |                    25 |                     25 |                            25 |                             25 |           25 |

# TODO put Nomatim link inside

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
