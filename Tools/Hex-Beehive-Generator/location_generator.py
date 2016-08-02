#!/usr/bin/env python

import math
import argparse
import LatLon
import itertools
import os


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-lat", "--lat",
        help="latitude",
        type=float,
        required=True
    )
    parser.add_argument(
        "-lon", "--lon",
        help="longitude",
        type=float,
        required=True
    )
    parser.add_argument(
        "-st", "--steps",
        help="steps",
        default=5,
        type=int)
    parser.add_argument(
        "-lp", "--leaps",
        help="like 'steps' but for workers instead of scans",
        default=3,
        type=int
    )
    parser.add_argument(
        "-o", "--output",
        default="../../beehive.sh",
        help="output file for the script"
    )
    parser.add_argument(
        "--accounts",
        help="List of your accounts, in csv [username],[password] format",
        default=None
    )
    parser.add_argument(
        "--auth",
        help="Auth method (ptc or google)",
        default="ptc"
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Print lat/lng to stdout for debugging",
        action='store_true',
        default=False
    )
    parser.add_argument(
        "--installdir",
        help="Installation directory (only used for Windows)",
        type=str,
        default="C:\\PokemonGo-Map"
    )

    command = parser.parse_args(namespace=GenerateLocations())

    return command


class GenerateLocations(argparse.Namespace):
    def __init__(self, **kwargs):
        self.r_hex = 52.5  # probably not correct
        self.steps = None
        self.installdir = None
        self.output = '../../beehive.sh'
        self.accounts = None
        self.auth = None
        self.verbose = False

        super(GenerateLocations, self).__init__(**kwargs)

    def setup_environment(self):
        # If we're running on windows set stuff up for that
        # Otherwise we're running on linux
        if os.name == 'nt':
            # ferkin Windows
            preamble = "taskkill /IM python.exe /F"
            pythonpath = "C:\\Python27\\Python.exe"
            branchpath = self.installdir
            executable = self.installdir + "\\runserver.py"
            auth_template = '-a {} -u {} -p "{}"'  # windows people want double-quoted passwords
            actual_worker_params = '{auth} -ns -l "{lat}, {lon}" -st {steps}'
            self.worker_template = 'Start "{{threadname}}" /d {branchpath} /MIN {pythonpath} {executable} {actual_params}\nping 127.0.0.1 -n 6 > nul\n\n'.format(
                branchpath=branchpath,
                pythonpath=pythonpath,
                executable=executable,
                actual_params=actual_worker_params
            )
            actual_server_params = '-os -l "{lat}, {lon}"'
            server_template = 'Start "Server" /d {branchpath} /MIN {pythonpath} {executable} {actual_params}\nping 127.0.0.1 -n 6 > nul\n\n'.format(
                branchpath=branchpath,
                pythonpath=pythonpath,
                executable=executable,
                actual_params=actual_server_params
            )
            if self.output == "../../beehive.sh":
                self.output = "../../beehive.bat"
        else:
            self.preamble = "#!/usr/bin/env bash"
            self.server_template = "nohup python runserver.py -os -l '{lat}, {lon}' &\n"
            self.worker_template = "sleep 0.5; nohup python runserver.py -ns -l '{lat}, {lon}' -st {steps} {auth} &\n"
            auth_template = "-a {} -u {} -p '{}'"  # unix people want single-quoted passwords

        if self.accounts is not None:
            print("Reading usernames/passwords from {}".format(self.accounts))
            account_fh = open(self.accounts)
            account_fields = [line.split(",") for line in account_fh]
            self.accounts = [auth_template.format(self.auth, line[0].strip(), line[1].strip()) for line in
                             account_fields]
        else:
            self.accounts = [""]

    def prepare_script(self):
        self.output_fh = file(self.output, "wb")
        os.chmod(self.output, 0o755)
        self.output_fh.write(self.preamble + "\n")
        self.output_fh.write(self.server_template.format(lat=self.lat, lon=self.lon))

    def generate_locations(self):
        radius = 6378137.0
        r_hex = 52.5
        steps = self.steps
        rings = self.leaps
        latitude = self.lat
        longitude = self.lon
        w_worker = (
                       2 * steps - 1) * r_hex  # convert the step limit of the worker into the r radius of the hexagon in meters?
        d = 2.0 * w_worker / 1000.0  # convert that into a diameter and convert to gps scale
        d_s = d

        brng_s = 0.0
        brng = 0.0
        mod = math.degrees(math.atan(1.732 / (6 * (steps - 1) + 3)))

        total_workers = 1

        locations = [LatLon.LatLon(LatLon.Latitude(0), LatLon.Longitude(0))] * ((((rings * (
            rings - 1)) / 2) * 6) + 1)  # this calculates how many workers there will be and initialises the list
        locations[0] = LatLon.LatLon(
            LatLon.Latitude(latitude),
            LatLon.Longitude(longitude)
        )  # set the latlon for worker 0 from cli args

        for i in range(1, rings):
            total_workers += 6 * i

        turns = 0  # number of turns made in this ring (0 to 6)
        turn_steps = 0  # number of cells required to complete one turn of the ring
        turn_steps_so_far = 0  # current cell number in this side of the current ring

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
                C = math.radians(60.0)  # inside angle of a regular hexagon
                a = d_s / radius * 2.0 * math.pi  # in radians get the arclength of the unit circle covered by d_s
                b = turn_steps_so_far * d_s / turn_steps / radius * 2.0 * math.pi  # percentage of a
                # the first spherical law of cosines gives us the length of side c from known angle C
                c = math.acos(math.cos(a) * math.cos(b) + math.sin(a) * math.sin(b) * math.cos(C))
                # turnsteps here represents ring number because yay coincidence always the same. multiply by derived arclength and convert to meters
                d = turn_steps * c * radius / 2.0 / math.pi
                # from the first spherical law of cosines we get the angle A from the side lengths a b c
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
        location_and_auth = [(i, j) for i, j in itertools.izip(locations, itertools.cycle(self.accounts))]

        for i, (location, auth) in enumerate(location_and_auth):
            threadname = "Movable{}".format(i)
            self.output_fh.write(
                self.worker_template.format(
                    lat=location.lat,
                    lon=location.lon,
                    steps=steps,
                    auth=auth,
                    threadname=threadname
                )
            )
            if self.verbose:
                print("{}, {}".format(location.lat, location.lon))

    def run(self):
        self.setup_environment()
        print("Generating beehive script to {}".format(self.output))
        self.prepare_script()
        self.generate_locations()


def main():
    generate = parseargs()
    generate.run()


if __name__ == '__main__':
    main()
