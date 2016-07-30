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
from s2sphere import CellId, LatLng
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
    
def get_cellid(lat, long):
    origin = CellId.from_lat_lng(LatLng.from_degrees(lat, long)).parent(15)
    walk = [origin.id()]

    # 10 before and 10 after
    next = origin.next()
    prev = origin.prev()
    for i in range(10):
        walk.append(prev.id())
        walk.append(next.id())
        next = next.next()
        prev = prev.prev()
    return ''.join(map(encode, sorted(walk)))

def encode(cellid):
    output = []
    encoder._VarintEncoder()(output.append, cellid)
    return ''.join(output)
