import math
import argparse
import LatLon
import itertools
import os

parser = argparse.ArgumentParser()
parser.add_argument("-lat", "--lat", help="latitude", type=float, required=True)
parser.add_argument("-lon", "--lon", help="longitude", type=float, required=True)
parser.add_argument("-st", "--steps", help="steps", default=5, type=int)
parser.add_argument("-lp", "--leaps", help="like 'steps' but for workers instead of scans", default=3, type=int)
parser.add_argument("-o", "--output", default="../../beehive.sh", help="output file for the script")
parser.add_argument("--accounts", help="List of your accounts, in csv [username],[password] format", default=None)
parser.add_argument("--auth", help="Auth method (ptc or google)", default="ptc")
parser.add_argument("-v", "--verbose", help="Print lat/lng to stdout for debugging", action='store_true', default=False)
parser.add_argument("--windows", help="Generate a bat file for Windows", action='store_true', default=False)
parser.add_argument("--installdir", help="Installation directory (only used for Windows)", type=str, default="C:\\PokemonGo-Map")

preamble = "#!/usr/bin/env bash"
server_template = "nohup python runserver.py -os -l '{lat} {lon}' &\n"
worker_template = "sleep 0.5; nohup python runserver.py -ns -l '{lat} {lon}' -st {steps} {auth} &\n"
auth_template = "-a {} -u {} -p '{}'"  # unix people want single-quoted passwords

R = 6378137.0
r_hex = 52.5  # probably not correct

args = parser.parse_args()
steps = args.steps
rings = args.leaps

if args.windows:
    # ferkin Windows
    preamble = "taskkill /IM python.exe /F"
    pythonpath = "C:\\Python27\\Python.exe"
    branchpath = args.installdir
    executable = args.installdir + "\\runserver.py"
    auth_template = '-a {} -u {} -p "{}"'  # windows people want double-quoted passwords
    actual_worker_params = '{auth} -ns -l "{lat} {lon}" -st {steps}'
    worker_template = 'Start "{{threadname}}" /d {branchpath} /MIN {pythonpath} {executable} {actual_params}\nping 127.0.0.1 -n 6 > nul\n\n'.format(
        branchpath=branchpath, pythonpath=pythonpath, executable=executable, actual_params = actual_worker_params
    )
    actual_server_params = '-os -l "{lat} {lon}"'
    server_template = 'Start "Server" /d {branchpath} /MIN {pythonpath} {executable} {actual_params}\nping 127.0.0.1 -n 6 > nul\n\n'.format(
        branchpath=branchpath, pythonpath=pythonpath, executable=executable, actual_params = actual_server_params
    )
    if args.output == "../../beehive.sh":
        args.output = "../../beehive.bat"

if args.accounts:
    print("Reading usernames/passwords from {}".format(args.accounts))
    account_fh = open(args.accounts)
    account_fields = [line.split(",") for line in account_fh]
    accounts = [auth_template.format(args.auth, line[0].strip(), line[1].strip()) for line in account_fields]
else:
    accounts = [""]

print("Generating beehive script to {}".format(args.output))
output_fh = file(args.output, "wb")
os.chmod(args.output, 0o755)
output_fh.write(preamble + "\n")
output_fh.write(server_template.format(lat=args.lat, lon=args.lon))

w_worker = (2 * steps - 1) * r_hex
d = 2.0 * w_worker / 1000.0
d_s = d

brng_s = 0.0
brng = 0.0
mod = math.degrees(math.atan(1.732 / (6 * (steps - 1) + 3)))

total_workers = 1

for i in range(1, rings):
    total_workers += 6 * i

locations = [LatLon.LatLon(LatLon.Latitude(0), LatLon.Longitude(0))] * total_workers
locations[0] = LatLon.LatLon(LatLon.Latitude(args.lat), LatLon.Longitude(args.lon))

turns = 0               # number of turns made in this ring (0 to 6)
turn_steps = 0          # number of cells required to complete one turn of the ring
turn_steps_so_far = 0   # current cell number in this side of the current ring


for i in range(1, total_workers):
    if turns == 6 or turn_steps == 0:
        # we have completed a ring (or are starting the very first ring)
        turns = 0
        turn_steps += 1
        turn_steps_so_far = 0

    if turn_steps_so_far == 0:
        brng = brng_s
        loc = locations[0]
        d = turn_steps * d
    else:
        loc = locations[0]
        C = math.radians(60.0)
        a = d_s / R * 2.0 * math.pi
        b = turn_steps_so_far * d_s / turn_steps / R * 2.0 * math.pi
        c = math.acos(math.cos(a) * math.cos(b) + math.sin(a) * math.sin(b) * math.cos(C))
        d = turn_steps * c * R / 2.0 / math.pi
        A = math.acos((math.cos(b) - math.cos(a) * math.cos(c)) / (math.sin(c) * math.sin(a)))
        brng = 60 * turns + math.degrees(A)

    loc = loc.offset(brng + mod, d)
    locations[i] = loc
    d = d_s

    turn_steps_so_far += 1
    if turn_steps_so_far >= turn_steps:
        # make a turn
        brng_s += 60.0
        brng = brng_s
        turns += 1
        turn_steps_so_far = 0

# if accounts list was provided, match each location with an account
# reusing accounts if required
location_and_auth = [(i, j) for i, j in itertools.izip(locations, itertools.cycle(accounts))]

for i, (location, auth) in enumerate(location_and_auth):
    threadname = "Movable{}".format(i)
    output_fh.write(worker_template.format(lat=location.lat, lon=location.lon, steps=args.steps, auth=auth, threadname=threadname))
    if args.verbose:
        print("{}, {}".format(location.lat, location.lon))
