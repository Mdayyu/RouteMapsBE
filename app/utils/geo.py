from math import radians, sin, cos, sqrt, atan2

def haversine_m(p1, p2):
    R = 6371000  # radius bumi (meter)
    lat1, lon1 = map(radians, p1)
    lat2, lon2 = map(radians, p2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2)
        * sin(dlon / 2) ** 2
    )
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))
