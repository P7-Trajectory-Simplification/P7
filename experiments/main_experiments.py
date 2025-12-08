import argparse
import json
import os
import time

from algorithms.dead_reckoning import DeadReckoning
from algorithms.dp import DouglasPeucker
from algorithms.squish import Squish
from algorithms.squish_e import SquishE
from algorithms.squish_reckoning import SquishReckoning
from algorithms.uniform_sampling import UniformSampling

from algorithms.great_circle_math import (
    great_circle_distance,
    get_final_bearing,
    predict_sphere_movement,
    point_to_great_circle,
)
from algorithms.ellipsoid_math import (
    point_to_geodesic,
    geodesic_final_bearing,
    geodesic_prediction,
    geodesic_length,
)
from error_metrics.comp_ratio import comp_ratio
from error_metrics.newped import ped_single_route_vectorized as ped
from error_metrics.newsed import sed_single_route_vectorized as sed
from experiments.experiment_data import read_trajectory_from_json

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--data_file_path", required=True, type=str)

    arg_parser.add_argument("--algorithm-name", required=True, type=str)
    arg_parser.add_argument(
        "--params", required=True, type=str
    )  # Should be string to be parsed as dict
    arg_parser.add_argument("--math", required=True, type=str)  # := circle | ellipsoid

    args = arg_parser.parse_args()

    data_file_path = args.data_file_path
    algorithm_name = args.algorithm_name
    params = json.loads(args.params.replace("\\", ""))
    math = args.math

    if math == "circle":
        math_args = {
            "point_to_point_distance": great_circle_distance,
            "predict_sphere_movement": predict_sphere_movement,
            "get_final_bearing": get_final_bearing,
            "point_to_line_distance": point_to_great_circle,
        }
    else:  # ellipsoid
        math_args = {
            "point_to_point_distance": geodesic_length,
            "predict_sphere_movement": geodesic_prediction,
            "get_final_bearing": geodesic_final_bearing,
            "point_to_line_distance": point_to_geodesic,
        }
    data_file_path = data_file_path.replace("\\", "/")
    trajectory = read_trajectory_from_json(os.path.join("experiments", data_file_path))

    simplifier_classes = {
        "DR": DeadReckoning,
        "DP": DouglasPeucker,
        "SQUISH": Squish,
        "SQUISH_E": SquishE,
        "UNIFORM_SAMPLING": UniformSampling,
        "SQUISH_RECKONING": SquishReckoning,
    }

    simplifier = simplifier_classes[algorithm_name].from_params(params, math_args)

    start_time = time.time()
    if simplifier.mode == "online":
        for i, point in enumerate(trajectory):
            simplifier.append_point(point)
            simplifier.simplify()
    else:  # batch mode
        for point in trajectory:
            simplifier.append_point(point)
        simplifier.simplify()
    end_time = time.time()
    run_time = end_time - start_time
    run_time_pr_point = len(trajectory) / run_time
    ped_avg, _, _ = ped(trajectory, simplifier.trajectory, math_args)
    sed_avg, _, _ = sed(trajectory, simplifier.trajectory, math_args)
    compression_ratio = comp_ratio(len(trajectory), len(simplifier.trajectory))

    print(
        "algorithm_name:"
        + algorithm_name
        + ","
        + "math:"
        + math
        + ","
        + "ped_avg:"
        + str(ped_avg)
        + ","
        + "sed_avg:"
        + str(sed_avg)
        + ","
        + "comp_ratio:"
        + str(compression_ratio)
        + ","
        + "run_time:"
        + str(run_time_pr_point),
        flush=True,
    )
