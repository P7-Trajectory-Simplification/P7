import json
from concurrent.futures import ProcessPoolExecutor
from flask import Flask, request
from flask import render_template

from algorithms.dead_reckoning import run_dr
from algorithms.dp import run_dp
from algorithms.isolate_routes import assign_routes, isolate_routes
from algorithms.squish import run_squish
from algorithms.squish_reckoning import run_sr
from algorithms.squish_e import run_squish_e
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
import json

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


def run_algorithms(
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
    return response


def routes_to_list(routes: list[Route]) -> list[list[tuple[float, float, datetime]]]:
    return [route.to_list() for route in routes]


algorithms_mappings = {
    'DR': run_dr,
    'DP': run_dp,
    'SQUISH': run_squish,
    'SQUISH_E': run_squish_e,
    'SQUISH_RECKONING': run_sr,
}


def get_error_metrics(
    raw_routes: list[Route], simplified_routes: list[Route]
) -> list[float]:
    error_metrics = []
    ped_avg, ped_max = ped_results(raw_routes, simplified_routes)
    sed_avg, sed_max = sed_results(raw_routes, simplified_routes)
    comp_ratio = comp_ratio_results(raw_routes, simplified_routes)
    error_metrics = [ped_avg, ped_max, sed_avg, sed_max, comp_ratio]
    return error_metrics


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


# the last end time we received (beginning at epoch just to have something)
# we will use this value as the start_time when retrieving from the database
# unless the start_time received from the website changes, at which point we will use that instead
last_end_time = datetime(0, 0, 0)

# TODO ensure the database does not fetch logs at the start time, only those between the start and end time and at the end time

"""

# SECTION new run_algorithms stuff
simplifiers = {}  # type: dict[int, list[Simplifier]]


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
"""


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
    # TODO this should probably differentiate between routes
