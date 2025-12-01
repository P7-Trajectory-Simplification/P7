import os
from pathlib import Path

from analyze_results_math import process_results_math
from analyze_results_jobs import process_results_jobs


def sanitize_line(line: str):
    return line.replace("[0]: ", "").replace("\n", "").replace("(", "").replace(")", "")


base_dir = Path(__file__).resolve().parent  # .../P7/experiments
results_dir = os.path.join(base_dir, "jobs\\logs_jobs")

results = []

for subdir, dirs, files in os.walk(results_dir):
    for file in files:
        if not file.startswith("output_"):
            continue
        result = {
            "math": "",
            "algorithm_name": "",
            "ped_avg": 0.0,
            "ped_max": 0.0,
            "sed_avg": 0.0,
            "sed_max": 0.0,
            "comp_ratio": 0.0,
            "run_time": 0.0,
        }
        math = file.split("_")[-1].replace(".log", "")
        result["math"] = math
        with open(os.path.join(results_dir, file), "r") as f:
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

results.sort(key=lambda x: (x["comp_ratio"]))


# process_results_math(results)
process_results_jobs(results)
