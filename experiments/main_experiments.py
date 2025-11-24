import argparse
from app import run_algorithms
from algorithms.great_circle_math import great_circle_distance, get_final_bearing, predict_sphere_movement, point_to_great_circle
from algorithms.ellipsoid_math import point_to_geodesic, geodesic_final_bearing, geodesic_prediction, geodesic_length


algorithm_names = [
          'DP'
            'DR'
            'SQUISH'
            'SQUISH_E'
            'UNIFORM_SAMPLING'
            'SQUISH_RECKONING'
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--imo", type=int)
    parser.add_argument("--start-time", required=True, type=str)
    parser.add_argument("--end-time", required=True, type=str)

    parser.add_argument("--algorithm-names", required=True, type=str)
    parser.add_argument("--params", required=True, type=str) # Should be string to be parsed as dict
    parser.add_argument("--math", required=True, type=str) # := circle | ellipsoid

    args = parser.parse_args()

    imo = args.imo
    start_time = args.start_time
    end_time = args.end_time
    algorithm_names = args.algorithm_names.split(",")
    params = eval(args.params)
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

    run_algorithms(
        algorithm_names=algorithm_names,
        start_time=start_time,
        end_time=end_time,
        params=params,
        imos=imo,
        math=math_args
    )