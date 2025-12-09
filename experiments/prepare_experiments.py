import os

from matplotlib.pyplot import switch_backend

from experiments.experiment_data import (
    download_trajectories_from_db,
    read_trajectory_from_json,
)
from experiments.job import Job


def prepare_math_comparison():
    """
    Prepares the environment for math comparison experiments.
    This may include setting up directories, loading datasets,
    and initializing parameters.
    """
    # Create directories for results
    print("Preparing math comparison experiments...")
    print("Creating directories...")
    os.makedirs("results/math_comparison", exist_ok=True)

    print("Downloading dataset...")
    if os.path.exists("results/math_comparison/data"):
        print("Math comparison data directory already exists. Skipping..")
    else:
        # Download dataset from db
        os.makedirs("results/math_comparison/data", exist_ok=True)
        download_trajectories_from_db(
            num_trajectories=50,
            data_directory="results/math_comparison/data",
            min_points=20000,
            max_points=50000,
        )

    print("Generating experiment jobs...")
    if os.path.exists("results/math_comparison/experiments"):
        print("Math comparison experiments directory already exists. Skipping..")
    else:
        os.makedirs("results/math_comparison/experiments", exist_ok=True)
        os.makedirs("results/math_comparison/experiments/logs", exist_ok=True)
        generate_math_comparison_experiments()
    print("Done generating experiment jobs.")


def generate_math_comparison_experiments():
    experiment_dir = "results/math_comparison"
    for compression_rate in [3, 4, 5, 7, 10, 15, 25, 50]:
        generate_experiments(experiment_dir, "SQUISH_E", compression_rate, "circle")
        generate_experiments(experiment_dir, "SQUISH_E", compression_rate, "ellipsoid")


def prepare_algorithm_comparison():
    """
    Prepares the environment for algorithm comparison experiments.
    This may include setting up directories, loading datasets,
    and initializing parameters.
    """
    # Create directories for results
    print("Preparing algorithm comparison experiments...")
    print("Creating directories...")
    os.makedirs("results/algorithm_comparison", exist_ok=True)

    print("Downloading dataset...")
    if os.path.exists("results/algorithm_comparison/data"):
        print("Algorithm comparison data directory already exists. Skipping..")
    else:
        # Download dataset from db
        os.makedirs("results/algorithm_comparison/data", exist_ok=True)
        download_trajectories_from_db(
            num_trajectories=50,
            data_directory="results/algorithm_comparison/data",
            min_points=20000,
            max_points=50000,
        )

    print("Generating experiment jobs...")
    if os.path.exists("results/algorithm_comparison/experiments"):
        print("Algorithm comparison experiments directory already exists. Skipping..")
    else:
        os.makedirs("results/algorithm_comparison/experiments", exist_ok=True)
        os.makedirs("results/algorithm_comparison/experiments/logs", exist_ok=True)
        generate_algorithm_comparison_experiments()
    print("Done generating experiment jobs.")


def generate_algorithm_comparison_experiments():
    experiment_dir = "results/algorithm_comparison"
    # 3 means we keep 1 out of every 3 points, 4 means we keep 1 out of every 4 points, etc.
    for compression_rate in [3, 4, 5, 7, 10, 15, 25, 50]:
        generate_experiments(experiment_dir, "SQUISH_E", compression_rate, "circle")
        generate_experiments(
            experiment_dir, "UNIFORM_SAMPLING", compression_rate, "circle"
        )
        generate_experiments(experiment_dir, "SQUISH", compression_rate, "circle")
        generate_experiments(
            experiment_dir, "SQUISH_RECKONING", compression_rate, "circle"
        )


def calc_buff_size(compression_rate: int, num_points: int) -> int:
    return max(2, num_points // compression_rate)


def make_params_dict(algorithm: str, rate: int, num_points: int) -> dict:
    if algorithm == "UNIFORM_SAMPLING":
        return {"sampling_rate": rate}
    elif algorithm == "SQUISH_E":
        return {"low_comp": rate, "max_sed": 0}
    else:
        return {"buff_size": calc_buff_size(rate, num_points)}


def generate_experiments(
    experiment_directory: str,
    algorithm: str,
    compression_rate: int,
    math: str,
    additional_info: str = "",
):
    experiment_files_directory = os.path.join(experiment_directory, "experiments")
    data_directory = os.path.join(experiment_directory, "data")
    data_files = os.listdir(data_directory)
    for file_name in data_files:
        num_of_experiment_files = len(os.listdir(experiment_files_directory))
        data_file_path = os.path.join(data_directory, file_name)
        trajectory = read_trajectory_from_json(data_file_path)

        param = make_params_dict(algorithm, compression_rate, len(trajectory))

        job = Job(
            trajectory,
            algorithm,
            param,
            math,
            additional_info,
        )
        job.generate_job(
            experiment_files_directory, data_file_path, num_of_experiment_files
        )


if __name__ == "__main__":
    prepare_algorithm_comparison()
    prepare_math_comparison()
