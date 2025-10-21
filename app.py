from flask import Flask, request
from flask import render_template

from algorithms.dead_reckoning import run_dr
from algorithms.dp import run_dp
from algorithms.isolate_routes import isolate_routes
from algorithms.squish import run_squish
from algorithms.squish_e import run_squish_e
from classes.route import Route
from data.database import get_all_vessels
from classes.vessel import Vessel
from datetime import datetime
from data.vessel_cache import get_data_from_cache
from typing import Callable
from error_metrics.sed import sed_results
from error_metrics.ped import ped_results

app = Flask(__name__)

def run_algorithm(routes: list[Route], func: Callable) -> list[Route]:
    simplified_trajectories = []
    for route in routes:
        simplified_trajectories.append(func(route))
    return simplified_trajectories

def run_algorithms(algorithms: list, start_time: datetime, end_time: datetime, vessel: Vessel):
    vessel_logs = get_data_from_cache(vessel, start_time, end_time)
    routes = isolate_routes(vessel_logs)

    response = {
        alg: routes_to_list(run_algorithm(routes, func))
        if alg in algorithms and func is not None
        else []
        for alg, func in algorithms_mappings.items()
    }

    response['raw'] = routes_to_list(routes)

    return response


def routes_to_list(routes: list[Route]) -> list[list[tuple[float, float, datetime]]]:
    return [route.to_list() for route in routes]


algorithms_mappings = {
    'DR': run_dr,
    'DP': run_dp,
    'SQUISH': run_squish,
    'SQUISH_E': run_squish_e
}

def get_error_metrics(raw_routes: list[dict], simplified_routes):
    error_metrics = []
    ped_avg, ped_max = ped_results(raw_routes, simplified_routes)
    sed_avg, sed_max = sed_results(raw_routes, simplified_routes)
    error_metrics = [ped_avg, ped_max, sed_avg, sed_max]
    return error_metrics

@app.route('/')
def index():
    return render_template('index.html.jinja', algorithms=algorithms_mappings.keys())


@app.route('/algorithm')
def get_algorithms():
    algorithms_req = request.args.get('algorithms')
    start_date_req = request.args.get('start_date')
    end_date_req = request.args.get('end_date')

    algorithms = algorithms_req.split(',')
    start_time_dt = datetime.strptime(start_date_req, '%Y-%m-%d')
    end_time_dt = datetime.strptime(end_date_req, '%Y-%m-%d %H:%M:%S')

    vessel = get_all_vessels()[125] # Example vessel

    print("Request for:", algorithms, start_time_dt, end_time_dt, vessel.name)

    return run_algorithms(algorithms, start_time_dt, end_time_dt, vessel)
