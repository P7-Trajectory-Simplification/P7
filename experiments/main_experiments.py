import argparse
import json
import os
import time
from dateutil import parser

from app import simplifier_classes, get_error_metrics
from algorithms.great_circle_math import great_circle_distance, get_final_bearing, predict_sphere_movement, point_to_great_circle
from algorithms.ellipsoid_math import point_to_geodesic, geodesic_final_bearing, geodesic_prediction, geodesic_length
from experiments.find_routes import load_route_data_from_json

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--imo", type=int)
    arg_parser.add_argument("--start-time", required=True, type=str)
    arg_parser.add_argument("--end-time", required=True, type=str)

    arg_parser.add_argument("--algorithm-name", required=True, type=str)
    arg_parser.add_argument("--params", required=True, type=str) # Should be string to be parsed as dict
    arg_parser.add_argument("--math", required=True, type=str) # := circle | ellipsoid

    args = arg_parser.parse_args()

    imo = args.imo
    start_time = parser.isoparse(args.start_time)
    end_time = parser.isoparse(args.end_time)
    algorithm_name = args.algorithm_name
    params = json.loads(args.params.replace("\\", ""))
    math = args.math

    if math == "circle":
        math_args = {
            "point_to_point_distance": great_circle_distance,
            "predict_sphere_movement": predict_sphere_movement,
            "get_final_bearing": get_final_bearing,
            "point_to_line_distance": point_to_great_circle
        }
    else: # ellipsoid
        math_args = {
            "point_to_point_distance": geodesic_length,
            "predict_sphere_movement": geodesic_prediction,
            "get_final_bearing": geodesic_final_bearing,
            "point_to_line_distance": point_to_geodesic
        }
    filename = f"imo_{imo}_start_{start_time.date()}_end_{end_time.date()}.json"
    trajectory = load_route_data_from_json(filename)
    simplifier = simplifier_classes[algorithm_name].from_params(
        params,
        math_args
    )

    start_time = time.time()
    for point in trajectory:
        simplifier.append_point(point)
        simplifier.simplify()
    end_time = time.time()
    run_time = end_time - start_time

    error_metrics = get_error_metrics(
        {0: trajectory},
        {0: simplifier.trajectory},
        math_args
    )

    ped_avg, ped_max, sed_avg, sed_max, comp_ratio = error_metrics
    print(
        "algorithm_name:"+algorithm_name+','+
        "math:"+math+','+
        "ped_avg:"+str(ped_avg)+','+
        "ped_max:"+str(ped_max)+','+
        "sed_avg:"+str(sed_avg)+','+
        "sed_max:"+str(sed_max)+','+
        "comp_ratio:"+str(comp_ratio)+','+
        "run_time:"+str(run_time)+','+
        "params:"+str(args.params)+'\n'
    , flush=True)