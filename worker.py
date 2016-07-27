# -*- coding: utf-8 -*-
from datetime import datetime
import argparse
import logging
import os
import random
import sys
import threading
import time

from pgoapi import (
    exceptions as pgoapi_exceptions,
    PGoApi,
    utilities as pgoapi_utils,
)

import config
import db
import utils


pokemons = {}
workers = {}
local_data = threading.local()
# api.local_data = local_data


def configure_logger(filename='worker.log'):
    logging.basicConfig(
        filename=filename,
        format=(
            '[%(asctime)s][%(threadName)10s][%(levelname)8s][L%(lineno)4d] '
            '%(message)s'
        ),
        style='{',
        level=logging.INFO,
    )

logger = logging.getLogger()


class Slave(threading.Thread):
    def __init__(
        self,
        group=None,
        target=None,
        name=None,
        worker_no=None,
        points=None,
    ):
        super(Slave, self).__init__(group, target, name)
        self.worker_no = worker_no
        local_data.worker_no = worker_no
        self.points = points
        self.count_points = len(self.points)
        self.step = 0
        self.cycle = 0
        self.seen = 0
        self.error_code = None
        self.api = PGoApi()

    def run(self):
        self.cycle = 1
        self.error_code = None

        # Login sequentially for PTC
        service = config.ACCOUNTS[self.worker_no][2]
        try:
            self.api.login(
                provider=service,
                username=config.ACCOUNTS[self.worker_no][0],
                password=config.ACCOUNTS[self.worker_no][1],
            )
        except pgoapi_exceptions.AuthException:
            self.error_code = 'LOGIN FAIL'
            return
        except pgoapi_exceptions.NotLoggedInException:
            self.error_code = 'BAD LOGIN'
            return
        except pgoapi_exceptions.ServerBusyOrOfflineException:
            self.error_code = 'RETRYING'
            time.sleep(random.randint(5, 10))
            start_worker(self.worker_no, self.points)
            return
        while self.cycle <= 3:
            self.main()
            self.cycle += 1
            if self.cycle <= 3:
                self.error_code = 'SLEEP'
                time.sleep(random.randint(30, 60))
                self.error_code = None
        self.error_code = 'RESTART'
        time.sleep(random.randint(30, 60))
        start_worker(self.worker_no, self.points)

    def main(self):
        session = db.Session()
        self.seen = 0
        for i, point in enumerate(self.points):
            logger.info('Visiting point %d (%s %s)', i, point[0], point[1])
            self.api.set_position(point[0], point[1], 0)
            cell_ids = pgoapi_utils.get_cell_ids(point[0], point[1])
            self.api.get_map_objects(
                latitude=pgoapi_utils.f2i(point[0]),
                longitude=pgoapi_utils.f2i(point[1]),
                cell_id=cell_ids
            )
            response_dict = self.api.call()
            now = time.time()
            map_objects = response_dict['responses'].get('GET_MAP_OBJECTS', {})
            pokemons = []
            if map_objects.get('status') == 1:
                for map_cell in map_objects['map_cells']:
                    for pokemon in map_cell.get('wild_pokemons', []):
                        pokemons.append(self.normalize_pokemon(pokemon, now))
            for raw_pokemon in pokemons:
                db.add_sighting(session, raw_pokemon)
                self.seen += 1
            logger.info('Point processed, %d Pokemons seen!', len(pokemons))
            session.commit()
            # Clear error code and let know that there are Pokemon
            if self.error_code and self.seen:
                self.error_code = None
            self.step += 1
        session.close()
        if self.seen == 0:
            self.error_code = 'NO POKEMON'

    @staticmethod
    def normalize_pokemon(raw, now):
        return {
            'encounter_id': raw['encounter_id'],
            'spawn_id': raw['spawn_point_id'],
            'pokemon_id': raw['pokemon_data']['pokemon_id'],
            'expire_timestamp': now + raw['time_till_hidden_ms'] / 1000.0,
            'lat': raw['latitude'],
            'lon': raw['longitude'],
        }

    @property
    def status(self):
        if self.error_code:
            msg = self.error_code
        else:
            msg = 'C{cycle},P{seen},{progress:.0f}%'.format(
                cycle=self.cycle,
                seen=self.seen,
                progress=(self.step / float(self.count_points) * 100)
            )
        return '[W{worker_no}: {msg}]'.format(
            worker_no=self.worker_no,
            msg=msg
        )


def get_status_message(workers, count, start_time, points_stats):
    messages = [workers[i].status.ljust(20) for i in range(count)]
    running_for = datetime.now() - start_time
    output = [
        'PokeMiner\trunning for {}'.format(running_for),
        '{len} workers, each visiting ~{avg} points per cycle '
        '(min: {min}, max: {max})'.format(
            len=len(workers),
            avg=points_stats['avg'],
            min=points_stats['min'],
            max=points_stats['max'],
        ),
        '',
    ]
    previous = 0
    for i in range(4, count + 4, 4):
        output.append('\t'.join(messages[previous:i]))
        previous = i
    return '\n'.join(output)


def start_worker(worker_no, points):
    logger.info('Worker (re)starting up!')
    worker = Slave(
        name='worker-%d' % worker_no,
        worker_no=worker_no,
        points=points
    )
    worker.daemon = True
    worker.start()
    workers[worker_no] = worker


def spawn_workers(workers, status_bar=True):
    points = utils.get_points_per_worker()
    start_date = datetime.now()
    count = config.GRID[0] * config.GRID[1]
    for worker_no in range(count):
        start_worker(worker_no, points[worker_no])
    lenghts = [len(p) for p in points]
    points_stats = {
        'max': max(lenghts),
        'min': min(lenghts),
        'avg': sum(lenghts) / float(len(lenghts)),
    }
    last_cleaned_cache = time.time()
    while True:
        now = time.time()
        if now - last_cleaned_cache > (15 * 60):
            db.CACHE.clean_expired()
        if status_bar:
            if sys.platform == 'win32':
                _ = os.system('cls')
            else:
                _ = os.system('clear')
            print get_status_message(workers, count, start_date, points_stats)
        time.sleep(0.5)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--no-status-bar',
        dest='status_bar',
        help='Log to console instead of displaying status bar',
        action='store_false',
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default=logging.INFO
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    if args.status_bar:
        configure_logger(filename='worker.log')
        logger.info('-' * 30)
        logger.info('Starting up!')
    else:
        configure_logger(filename=None)
    logger.setLevel(args.log_level)
    spawn_workers(workers, status_bar=args.status_bar)
