import math
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("-lat", "--lat", help="latitude")
parser.add_argument("-lon", "--lon", help="longitude")
parser.add_argument("-st", "--steps", help="steps")
parser.add_argument("-lp", "--leaps", help="like 'steps' but for workers instead of scans")

R = 6378137.0

r_hex = 149.9497/2.0

args = parser.parse_args()
st = (int)(args.steps)
wst = (int)(args.leaps)

w_worker = (2 * st - 1) * r_hex
d = 2 * w_worker

total_workers = 1

for i in range(1, wst):
    total_workers += 6*(i)


brng = math.radians(0)

lon = [0] * total_workers
lat = [0] * total_workers
lat[0] = math.radians((float)(args.lat))
lon[0] = math.radians((float)(args.lon))

turn_steps = 0
turn_steps_so_far = 0
turn_count = 0

jump_points = [0] * (wst + 1)
jump_points[0] = 0
jump_points[1] = 1
jump = 1
for i in range(2,wst + 1):
    jump_points[i] = jump_points[i-1] + 6 *(i-1)

for i in range(1, total_workers):

    lat1 = lat[i - 1]
    lon1 = lon[i - 1]
    
    if i in jump_points and jump > 0:
        lat1 = lat[jump_points[jump-1]]
        lon1 = lon[jump_points[jump-1]]
        jump += 1
        turn_steps += 1
        turn_steps_so_far = turn_steps
        brng = math.radians(0)
    lat2 = math.asin( math.sin(lat1)*math.cos(d/R) +
                      math.cos(lat1)*math.sin(d/R)*math.cos(brng))

    lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(d/R)*math.cos(lat1),
                             math.cos(d/R)-math.sin(lat1)*math.sin(lat2))

    lat[i] = lat2
    lon[i] = lon2
    if i in jump_points:
        brng = math.radians(60)
    if turn_steps_so_far == turn_steps:
        brng += math.radians(60.0)
        turn_steps_so_far = 0
    turn_steps_so_far += 1

for i in range(total_workers):
    print str(math.degrees(lat[i])) + ", " + str(math.degrees(lon[i]))
        
