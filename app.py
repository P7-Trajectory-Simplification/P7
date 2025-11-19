from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from flask import Flask, request
from flask import render_template
import numpy as np

from algorithms.dead_reckoning import DeadReckoning, run_dr
from algorithms.dp import DouglasPeucker, run_dp
from algorithms.isolate_routes import assign_routes, isolate_routes
from algorithms.squish import Squish, run_squish
from algorithms.squish_reckoning import SquishReckoning, run_sr
from algorithms.squish_e import SquishE, run_squish_e
from algorithms.uniform_sampling import UniformSampling, run_uniform_sampling
from classes.route import Route
from classes.simplifier import Simplifier
from classes.vessel_log import VesselLog
from data.database import get_all_vessels
from classes.vessel import Vessel
from datetime import datetime
from data.vessel_cache import get_data_from_cache
from typing import Callable
from error_metrics.comp_ratio import comp_ratio_results
from error_metrics.sed import sed_results
from error_metrics.ped import ped_results

app = Flask(__name__)


def run_algorithm(routes: list[Route], func: Callable, params: dict) -> list[Route]:
    simplified_trajectories = []
    for route in routes:
        simplified_trajectories.append(func(route, params))
    return simplified_trajectories


# Called by the multiprocessing executor
def multi_process_helper(multi_process_data: dict):
    alg = multi_process_data['alg']
    func = multi_process_data['func']
    routes = multi_process_data['routes']
    params = multi_process_data['params']
    if func is not None and routes is not None:
        simplified_routes = run_algorithm(routes, func, params)
        alg_route = routes_to_list(simplified_routes)
        error_metrics = get_error_metrics(routes, simplified_routes)
    else:
        alg_route = []
        error_metrics = []

    return alg, alg_route, error_metrics


# Combines data needed for multiprocessing into a list of dicts
def build_multi_process_data(
    func: Callable, routes: list[Route], algorithms: list[str], params: dict
) -> list[dict]:
    multiprocess_data = []
    for alg, func in algorithms_mappings.items():
        if alg in algorithms:
            multiprocess_data.append(
                {'func': func, 'alg': alg, 'routes': routes, 'params': params}
            )
        else:
            multiprocess_data.append(
                {'func': None, 'alg': alg, 'routes': None, 'params': params}
            )
    return multiprocess_data


'''def run_algorithms(
    algorithms: list,
    start_time: datetime,
    end_time: datetime,
    params: dict,
    vessel: Vessel,
):
    """Run the selected algorithms and return the resulting trajectories."""
    vessel_logs = get_data_from_cache(vessel, start_time, end_time)
    routes = assign_routes(vessel_logs)
    response = {}

    multiprocess_data = build_multi_process_data(algorithms, routes, algorithms, params)

    # Use ProcessPoolExecutor to run algorithms in parallel
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(multi_process_helper, multiprocess_data))
        for alg, alg_route, error_metrics in results:
            response[alg] = alg_route
            response[alg + '_error_metrics'] = error_metrics

    response['raw'] = routes_to_list(routes)
    return response'''


def routes_to_list(routes: list[Route]) -> list[list[tuple[float, float, datetime]]]:
    return [route.to_list() for route in routes]


algorithms_mappings = {
    'DR': run_dr,
    'DP': run_dp,
    'SQUISH': run_squish,
    'SQUISH_E': run_squish_e,
    'UNIFORM_SAMPLING': run_uniform_sampling,
    'SQUISH_RECKONING': run_sr,
}


def get_error_metrics(
    raw_routes: list[Route], simplified_routes: list[Route]
) -> list[float]:
    ped_avg, ped_max = ped_results(raw_routes, simplified_routes)
    sed_avg, sed_max = sed_results(raw_routes, simplified_routes)
    comp_ratio = comp_ratio_results(raw_routes, simplified_routes)
    return [ped_avg, ped_max, sed_avg, sed_max, comp_ratio]


@app.route('/')
def index():
    return render_template('index.html.jinja', algorithms=algorithms_mappings.keys())


@app.route('/algorithm', methods=['POST'])
def get_algorithms():
    data = request.get_json(force=True)

    if not data:
        return {"error": "Invalid JSON"}, 400

    params_req = data['params']
    start_date_req = data['start_date']
    end_date_req = data['end_date']

    algorithms = data['algorithms']
    start_time_dt = datetime.strptime(start_date_req, '%Y-%m-%d')
    end_time_dt = datetime.strptime(end_date_req, '%Y-%m-%d %H:%M:%S')

    vessel = get_all_vessels()[125]  # Example vessel

    print(
        "Request for:", algorithms, start_time_dt, end_time_dt, params_req, vessel.name
    )

    return run_algorithms(algorithms, start_time_dt, end_time_dt, params_req, vessel)


# SECTION new run_algorithms stuff
# the last end time we received (beginning at epoch just to have something)
# we will use this value as the start_time when retrieving from the database
# unless the start_time received from the website changes, at which point we will use that instead
last_end_time = datetime.fromtimestamp(0)

last_start_time = datetime.fromtimestamp(0)
'''
def prepare_processing(
    routes: dict[int, list[VesselLog]],
    algorithms: list[str],
    params: dict[str, float],  # FIXME unsure of this guy's type
) -> list[tuple[int, list[VesselLog], list[Simplifier]]]:
    global simplifiers
    for key, logs in routes.items():
        if key not in simplifiers:
            pass  # TODO create simplifiers based on the list of identifiers found in algorithms and the params
    return [(k, routes[k], simplifiers[k]) for k in routes]


def process_route(
    item: tuple[int, list[VesselLog], list[Simplifier]],
) -> tuple[int, list[Simplifier]]:
    key, logs, simplifiers = item
    for s in simplifiers:
        for l in logs:
            s.trajectory.append(l)
            s.simplify()
    return (key, [s.trajectory for s in simplifiers])


def finalize_response(
    results: list[tuple[int, list[Simplifier]]],
) -> dict[int, dict[str, list[VesselLog]]]:
    global simplifiers
    for key, ss in results:
        simplifiers[key] = ss
    return {
        k: {s.name: s.trajectory} for k, ss in results for s in ss
    }  # TODO add error metrics and a name field for simplifiers
'''

simplifiers = {}  # type: dict[int, list[Simplifier]]

simplifier_classes = {
    'DR': DeadReckoning,
    'DP': DouglasPeucker,
    'SQUISH': Squish,
    'SQUISH_E': SquishE,
    'UNIFORM_SAMPLING': UniformSampling,
    'SQUISH_RECKONING': SquishReckoning,
}

# this will accumulate all the points in all the routes over time. For use in error metric computation.
raw_routes = {}  # type: dict[int, list[VesselLog]]


def process_trajectories(routes: dict[int, list[VesselLog]], algorithm_names, params):
    '''Create the necessary simplifiers according to the given params and append the given logs to them, simplifying each time.'''
    for route_id, logs in routes.items():
        if route_id not in simplifiers:
            # create the necessary simplifiers for the given route and make sure the logs are recorded
            simplifiers[route_id] = [
                simplifier_classes[name].from_params(params) for name in algorithm_names
            ]
            raw_routes[route_id] = []
        raw_routes[route_id] += logs
        for simplifier in simplifiers[route_id]:
            for log in logs:
                simplifier.trajectory.append(log)
                simplifier.simplify()


'''
def simplifiers_to_list(
    # given a dict mapping integers to lists of simplifiers,
    # return a list of lists of tuples describing the trajectories of the simplifiers
    # for use in a request response.
    simplifiers: dict[int, list[Simplifier]],
) -> list[list[tuple[float, float, datetime]]]:
    return [
        [(log.lat, log.lon, log.ts) for log in simplifier.trajectory]
        for simplifier_list in simplifiers.values()
        for simplifier in simplifier_list
    ]
    # TODO this should probably differentiate between routes, but the website would have to accomodate the new response format
'''


def run_algorithms(
    algorithm_names: list,
    start_time: datetime,
    end_time: datetime,
    params: dict,
    vessel: Vessel,
):
    '''Run the selected algorithms and return the resulting trajectories.'''
    global last_start_time
    global last_end_time
    if start_time == last_start_time:
        # If the requested start time is the same as it was last request,
        # just get the points between the last end time and the current end time.
        # This ensures that we don't grab points we've already processed.
        start_time = last_end_time
    else:
        # TODO if the start time has changed, we'll probably need to reset our simplifiers and error metrics.
        # REVIEW how to handle parameters changing? How to handle algorithms being enabled after some points have already been processed?
        last_start_time = start_time
    last_end_time = end_time
    print('Fetching logs...')
    vessel_logs = get_data_from_cache(vessel, start_time, end_time)
    print('Assigning routes...')
    routes = assign_routes(vessel_logs)
    response = {}

    # NOTE no multiprocessing for now
    # REVIEW how many calls to simplify() are needed to justify multiprocessing?
    print('Processing...')
    process_trajectories(routes, algorithm_names, params)

    # SECTION
    # NOTE this is extremely temporary: We know there's only one vessel, so there will only ever be one active route.
    # Therefore we can simply attribute any trajectory from a given simplifier to that vessel.
    print('Writing response...')
    error_metrics_placeholder = [0, 0, 0, 0, 0]
    for simplifier_list in simplifiers.values():
        for simplifier in simplifier_list:
            if simplifier.name not in response:
                response[simplifier.name] = []
                # append all trajectories simplified by this algorithm to the same part of the response
            response[simplifier.name].append(
                [(log.lat, log.lon, log.ts) for log in simplifier.trajectory]
            )
            response[simplifier.name + '_error_metrics'] = error_metrics_placeholder
    response['raw'] = [
        # NOTE that we are using the accumulated raw routes, and not just the logs for this iteration
        [(log.lat, log.lon, log.ts) for log in logs]
        for logs in raw_routes.values()
    ]
    for name in simplifier_classes.keys():
        if name not in response:
            response[name] = []

    #!SECTION
    print('Responding...')
    return response
    # TODO the trajectories given in the response should be identified by both a route ID and an algorithm name
    # and the frontend should be able to handle that
