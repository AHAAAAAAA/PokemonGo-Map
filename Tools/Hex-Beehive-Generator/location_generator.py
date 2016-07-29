import math
import argparse
import LatLon

parser = argparse.ArgumentParser()
parser.add_argument("-lat", "--lat", help="latitude")
parser.add_argument("-lon", "--lon", help="longitude")
parser.add_argument("-st", "--steps", help="steps")
parser.add_argument("-lp", "--leaps", help="like 'steps' but for workers instead of scans")

R = 6378137.0

r_hex = 75.0

args = parser.parse_args()
st = (int)(args.steps)
wst = (int)(args.leaps)

w_worker = (2 * st - 1) * r_hex
d = 2.0 * w_worker /1000.0
d_s = d
brng_s = 0.0
brng = 0.0
mod = math.degrees(math.atan(1.732/(6*(st-1)+3)))


total_workers = 1

for i in range(1, wst):
    total_workers += 6*(i)

locations = [LatLon.LatLon(LatLon.Latitude(0),LatLon.Longitude(0))] * total_workers
locations[0] = LatLon.LatLon(LatLon.Latitude(args.lat),LatLon.Longitude(args.lon))

turn_steps = 0
turn_steps_so_far = 0
turn_count = 0

jump_points = [0] * (wst + 1)
jump_points[0] = 0
jump_points[1] = 1
turns = 0
jump = 1
for i in range(2,wst + 1):
    jump_points[i] = jump_points[i-1] + 6 *(i-1)

for i in range(1, total_workers):
    if turns == 6 or turn_steps == 0:
        turn_steps += 1
        turn_steps_so_far = 0
    if turn_steps_so_far == 0:
        brng = brng_s
        loc = locations[0]
	d = (turn_steps) * d
    else:
	loc = locations[0]
        C = math.radians(60.0)
        a = d_s / R * 2.0 * math.pi
	b = turn_steps_so_far * d_s / turn_steps / R * 2.0 * math.pi
        c = math.acos(math.cos(a) * math.cos(b) + math.sin(a) * math.sin(b) * math.cos(C))
	d = turn_steps * c * R / 2.0 / math.pi
	A = math.acos((math.cos(b) - math.cos(a) * math.cos(c))/(math.sin(c)*math.sin(a)))
        brng = 60 * turns + math.degrees(A)
    loc = loc.offset(brng + mod, d)
    locations[i] = loc
    d = d_s

    turn_steps_so_far += 1
    if turn_steps_so_far >= turn_steps:
        brng_s += 60.0
        brng = brng_s
        turns += 1
        turn_steps_so_far = 0
    
    

for i in range(total_workers):
    strloc = locations[i].to_string('D')
    print strloc[0] + ", " + strloc[1]
        
