from math import sqrt, sin, cos

a = 6378245.0
ee = 0.00669342162296594323
pi = 3.14159265358979324


def transform_from_wgs_to_gcj(wgs_loc):
    adjust_loc = Location("", "")
    if is_location_out_of_china(wgs_loc):
        adjust_loc = wgs_loc
    else:
        adjust_lat = transform_lat(wgs_loc.longitude - 105, wgs_loc.latitude - 35.0)
        adjust_lon = transform_long(wgs_loc.longitude - 105, wgs_loc.latitude - 35.0)
        rad_lat = wgs_loc.latitude / 180.0 * pi
        magic = sin(rad_lat)
        magic = 1 - ee * magic * magic
        sqrt_magic = sqrt(magic)
        adjust_lat = (adjust_lat * 180.0) / ((a * (1 - ee)) / (magic * sqrt_magic) * pi)
        adjust_lon = (adjust_lon * 180.0) / (a / sqrt_magic * cos(rad_lat) * pi)
        adjust_loc.latitude = wgs_loc.latitude + adjust_lat
        adjust_loc.longitude = wgs_loc.longitude + adjust_lon
    #print 'transfromed from ', wgs_loc, ' to ', adjust_loc
    return adjust_loc.latitude, adjust_loc.longitude


def is_location_out_of_china(wgs):
    if wgs.longitude < 72.004 or wgs.longitude > 137.8347 or wgs.latitude < 0.8293 or wgs.latitude > 55.8271:
        return True
    return False


def transform_lat(x, y):
    lat = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * sqrt(abs(x))
    lat += (20.0 * sin(6.0 * x * pi) + 20.0 * sin(2.0 * x * pi)) * 2.0 / 3.0
    lat += (20.0 * sin(y * pi) + 40.0 * sin(y / 3.0 * pi)) * 2.0 / 3.0
    lat += (160.0 * sin(y / 12.0 * pi) + 320 * sin(y * pi / 30.0)) * 2.0 / 3.0
    return lat


def transform_long(x, y):
    lon = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * sqrt(abs(x))
    lon += (20.0 * sin(6.0 * x * pi) + 20.0 * sin(2.0 * x * pi)) * 2.0 / 3.0
    lon += (20.0 * sin(x * pi) + 40.0 * sin(x / 3.0 * pi)) * 2.0 / 3.0
    lon += (150.0 * sin(x / 12.0 * pi) + 300.0 * sin(x / 30.0 * pi)) * 2.0 / 3.0
    return lon


class Location:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return "%8f,%8f" % (self.latitude, self.longitude)
