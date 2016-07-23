"""
pgoapi - Pokemon Go API
Copyright (c) 2016 tjado <https://github.com/tejado>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

Author: tjado <https://github.com/tejado>
"""

import struct
import re

from importlib import import_module
from s2sphere import LatLng, Cell, RegionCoverer, Cap
from google.protobuf.internal import encoder
from geopy.geocoders import GoogleV3


def f2i(float):
  return struct.unpack('<Q', struct.pack('<d', float))[0]

def f2h(float):
  return hex(struct.unpack('<Q', struct.pack('<d', float))[0])

def h2f(hex):
  return struct.unpack('<d', struct.pack('<Q', int(hex,16)))[0]

def to_camel_case(value):
  def camelcase():
    while True:
      yield str.capitalize

  c = camelcase()
  return "".join(c.next()(x) if x else '_' for x in value.split("_"))

def get_pos_by_name(location_name):
    prog = re.compile("^(\-?\d+\.\d+)?,\s*(\-?\d+\.\d+?)$")
    res = prog.match(location_name)
    latitude, longitude, altitude = None, None, None
    if res:
        latitude, longitude, altitude = float(res.group(1)), float(res.group(2)), 0
    elif location_name:
        geolocator = GoogleV3()
        loc = geolocator.geocode(location_name)
        if loc:
            latitude, longitude, altitude = loc.latitude, loc.longitude, loc.altitude

    return (latitude, longitude, altitude)


def get_class(cls):
    module_, class_ = cls.rsplit('.', 1)
    class_ = getattr(import_module(module_), class_)
    return class_

# cap height defaults to a circle of 100m (pokemon visible radius)
# you seem to always need 21 cells worth of coverage, but I have no idea why
def build_cap_coverage(lat, lng, cell_count=21, radius=100.0):
    # these are the zoom levels for s2cells
    min_zoom_level = 15
    max_zoom_level = 30

    # radius of the earth in meters
    R = 6378137.0;

    cap_height = ((radius/R)**2)/2
    axis = LatLng.from_degrees(lat, lng).to_point()
    cap = Cap.from_axis_height(axis, cap_height)

    coverer = RegionCoverer()
    coverer.min_level = min_zoom_level
    coverer.max_level = max_zoom_level
    coverer.max_cells = cell_count
    covering = list(coverer.get_covering(cap))
    while(len(covering) < cell_count):
        covering.append(covering[-1].next())
    return covering

def get_cellid(lat, long):
    cells = build_cap_coverage(lat, long)
    walk = map(lambda cell: cell.id(), cells)
    return ''.join(map(encode, walk))

def encode(cellid):
    output = []
    encoder._VarintEncoder()(output.append, cellid)
    return ''.join(output)
