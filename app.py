from flask import Flask, request
from flask import render_template

from algorithms.dead_reckoning import DeadReckoning
from algorithms.dp import DouglasPeucker
from algorithms.isolate_routes import assign_routes
from algorithms.squish import Squish
from algorithms.squish_reckoning import SquishReckoning
from algorithms.squish_e import SquishE
from algorithms.uniform_sampling import UniformSampling
from classes.simplifier import Simplifier
from classes.vessel_log import VesselLog
from data.database import get_all_vessels, get_vessel_logs
from datetime import datetime
from data.vessel_cache import get_data_from_cache
from error_metrics.comp_ratio import comp_ratio_results
from error_metrics.sed import sed_results
from error_metrics.ped import ped_results

app = Flask(__name__)

simplifier_classes = {
    "DR": DeadReckoning,
    "DP": DouglasPeucker,
    "SQUISH": Squish,
    "SQUISH_E": SquishE,
    "UNIFORM_SAMPLING": UniformSampling,
    "SQUISH_RECKONING": SquishReckoning,
}

# the last end time we received (beginning at epoch just to have something)
# we will use this value as the start_time when retrieving from the database
# unless the start_time received from the website changes, at which point we will use that instead
last_end_time = datetime.fromtimestamp(0)
last_start_time = datetime.fromtimestamp(0)

simplifiers = {}  # type: dict[int, dict[str, Simplifier]]

# this will accumulate all the points in all the routes over time. For use in error metric computation.
raw_routes = {}  # type: dict[int, list[VesselLog]]


def get_error_metrics(
    raw_routes: dict[int, list[VesselLog]],
    simplified_routes: dict[int, list[VesselLog]],
) -> list[float]:

    ped_avg, ped_max = ped_results(raw_routes, simplified_routes)
    sed_avg, sed_max = sed_results(raw_routes, simplified_routes)
    comp_ratio = comp_ratio_results(raw_routes, simplified_routes)
    return [ped_avg, ped_max, sed_avg, sed_max, comp_ratio]


def process_trajectories(
    routes: dict[int, list[VesselLog]],
    algorithm_names: list[str],
    params: dict[str, int],
):
    """Create the necessary simplifiers according to the given params and append the given logs to them, simplifying each time."""
    for id in routes.keys():
        if id not in raw_routes:
            raw_routes[id] = []

    for route_id, route_trajectory in routes.items():
        raw_routes[route_id] += route_trajectory

    for key in raw_routes.keys():
        simplifiers[key] = {}
        for name in algorithm_names:
            simplifiers[key][name] = simplifier_classes[name].from_params(params)
        for simplifier in simplifiers[key].values():
            for log in raw_routes[key]:
                simplifier.append_point(log)
                simplifier.simplify()


def run_algorithms(
    algorithm_names: list[str],
    start_time: datetime,
    end_time: datetime,
    params: dict[str, int],
    imos: list[int],
) -> dict[str, list[list[tuple[float, float, datetime]]]]:
    """Run the selected algorithms and return the resulting trajectories."""
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
    print("Fetching logs...")
    vessel_logs = get_vessel_logs(imos, start_time, end_time)
    print("Assigning routes...")
    routes = assign_routes(vessel_logs)
    response = {}

    # NOTE no multiprocessing for now
    # REVIEW how many calls to simplify() are needed to justify multiprocessing?
    print("Processing...")
    process_trajectories(routes, algorithm_names, params)

    # SECTION
    # NOTE this is extremely temporary: We know there's only one vessel, so there will only ever be one active route.
    # Therefore we can simply attribute any trajectory from a given simplifier to that vessel.
    print("Writing response...")
    for simplifier_dict in simplifiers.values():
        for simplifier in simplifier_dict.values():
            if simplifier.name not in response:
                response[simplifier.name] = []
                # append all trajectories simplified by this algorithm to the same part of the response
            response[simplifier.name].append(
                [(log.lat, log.lon, log.ts) for log in simplifier.trajectory]
            )
    response["raw"] = [
        # NOTE that we are using the accumulated raw routes, and not just the logs for this iteration
        [(log.lat, log.lon, log.ts) for log in logs]
        for logs in raw_routes.values()
    ]
    for name in algorithm_names:
        response[name + "_error_metrics"] = get_error_metrics(
            raw_routes,
            {
                route_id: simplifier_dict[name].trajectory
                for route_id, simplifier_dict in simplifiers.items()
            },
        )
    for name in simplifier_classes:
        if name not in response:
            response[name] = []

    # !SECTION
    print("Responding...")
    return response
    # TODO the trajectories given in the response should be identified by both a route ID and an algorithm name
    # and the frontend should be able to handle that


@app.route("/")
def index():
    return render_template("index.html.jinja", algorithms=simplifier_classes.keys())


@app.route("/algorithm", methods=["POST"])
def get_algorithms():
    data = request.get_json(force=True)

    if not data:
        return {"error": "Invalid JSON"}, 400

    params_req = data["params"]
    start_date_req = data["start_date"]
    end_date_req = data["end_date"]

    algorithms = data["algorithms"]
    start_time_dt = datetime.strptime(start_date_req, "%Y-%m-%d")
    end_time_dt = datetime.strptime(end_date_req, "%Y-%m-%d %H:%M:%S")

    imos = [get_all_vessels()[125].imo, get_all_vessels()[100].imo]

    print(
        "Request for:",
        algorithms,
        start_time_dt,
        end_time_dt,
        params_req,
        """vessel.name""",  # TODO print vessel names elsewhere, like when starting an experiment
    )
    return run_algorithms(algorithms, start_time_dt, end_time_dt, params_req, imos)


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
