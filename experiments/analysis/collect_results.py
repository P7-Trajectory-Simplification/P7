import os
from pathlib import Path

import numpy as np

from analyze_results_math import process_results_math
from analyze_results_jobs import process_results_jobs


def sanitize_line(line: str):
    return line.replace("[0]: ", "").replace("\n", "").replace("(", "").replace(")", "")


def collect_results(logs_dir: str) -> list[dict]:
    results = []

    for subdir, dirs, files in os.walk(logs_dir):
        for file in files:
            if not file.startswith("output_"):
                continue
            result = {
                "math": "",
                "algorithm_name": "",
                "ped_avg": 0.0,
                "sed_avg": 0.0,
                "comp_ratio": 0.0,
                "run_time": 0.0,
            }
            with open(os.path.join(logs_dir, file), "r") as f:
                content = f.read()
                content = sanitize_line(content)
                if content == "":
                    continue
                for pair in content.split(","):
                    key, value = pair.split(":", 1)
                    if value == "nan":
                        print("Found nan value in file:", file, "for key:", key)
                        value = 0.0
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                    result[key] = value
            results.append(result)
    return results


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent  # .../P7/experiments
    math_logs_dir = os.path.join(base_dir, "results/math_comparison/experiments/logs")
    algorithm_logs_dir = os.path.join(
        base_dir, "results/algorithm_comparison/experiments/logs"
    )

    math_results = collect_results(math_logs_dir)
    algorithm_results = collect_results(algorithm_logs_dir)
    math_results.sort(key=lambda x: (x["comp_ratio"]))
    algorithm_results.sort(key=lambda x: (x["comp_ratio"]))

    # process_results_math(math_results)
    process_results_jobs(algorithm_results)
