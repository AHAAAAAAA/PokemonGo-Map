import config


def get_map_center():
    """Returns center of the map"""
    lat = (config.MAP_END[0] + config.MAP_START[0]) / 2
    lon = (config.MAP_END[1] + config.MAP_START[1]) / 2
    return lat, lon


def get_start_coords(worker_no):
    """Returns center of square for given worker"""
    grid = config.GRID
    total_workers = grid[0] * grid[1]
    per_column = total_workers / grid[0]
    column = worker_no % per_column
    row = worker_no / per_column
    part_lat = (config.MAP_END[0] - config.MAP_START[0]) / float(grid[0])
    part_lon = (config.MAP_END[1] - config.MAP_START[1]) / float(grid[1])
    start_lat = config.MAP_START[0] + part_lat * row + part_lat / 2
    start_lon = config.MAP_START[1] + part_lon * column + part_lon / 2
    return start_lat, start_lon


def get_worker_coords(worker_no):
    """Returns start and end coords for given worker"""
    grid = config.GRID
    total_workers = grid[0] * grid[1]
    per_column = total_workers / grid[0]
    column = worker_no % per_column
    row = worker_no / per_column
    part_lat = (config.MAP_END[0] - config.MAP_START[0]) / float(grid[0])
    part_lon = (config.MAP_END[1] - config.MAP_START[1]) / float(grid[1])
    start_lat = config.MAP_START[0] + part_lat * row
    start_lon = config.MAP_START[1] + part_lon * column
    end_lat = start_lat + part_lat
    end_lon = start_lon + part_lon
    return (start_lat, start_lon), (end_lat, end_lon)


def float_range(start, end, step):
    if start > end:
        while end < start:
            yield start
            start += -step
    else:
        while start < end:
            yield start
            start += step


def get_worker_grid(worker_no):
    """Returns list of points that worker has to check"""
    start_coords = get_start_coords(worker_no)
    worker_coords = get_worker_coords(worker_no)
    points = []
    lat_gain = getattr(config, 'LAT_GAIN', 0.0015)
    # Go north!
    for lat in float_range(start_coords[0], worker_coords[0][0], lat_gain):
        # Go east!
        for lon in float_range(start_coords[1], worker_coords[0][1], 0.0025):
            points.append((lat, lon))
        # Go west!
        for lon in float_range(start_coords[1], worker_coords[1][1], 0.0025):
            points.append((lat, lon))
    # Go south!
    for lat in float_range(start_coords[0], worker_coords[1][0], lat_gain):
        # Go east!
        for lon in float_range(start_coords[1], worker_coords[0][1], 0.0025):
            points.append((lat, lon))
        # Go west!
        for lon in float_range(start_coords[1], worker_coords[1][1], 0.0025):
            points.append((lat, lon))
    return points
