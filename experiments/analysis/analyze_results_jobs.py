import matplotlib.pyplot as plt


def extract_lists(
    data: dict[str, dict[float, dict[str, float]]], extract_parameter: str
):

    x = []
    y_sed = []
    y_ped = []
    y_runtime = []
    for compression_rate, value in data[extract_parameter].items():
        x.append(compression_rate)
        y_sed.append(value["sed_avg"])
        y_ped.append(value["ped_avg"])
        y_runtime.append(value["run_time"])
    return x, y_sed, y_ped, y_runtime


def compile_results_jobs(
    results: list[dict],
) -> dict[str, dict[float, dict[str, list]]]:
    """
    Docstring for compile_results_jobs

    :param results: A list of result dictionaries containing the metrics "math", "algorithm_name", "ped_avg", "ped_max", "sed_avg", "sed_max", "run_time", and "comp_ratio"
    :type results: list[dict]
    :return: A dictionary mapping algorithm names to compression rates to metrics, where each metric maps to a list of its recorded values.
    Structure is therefore
        {
        "algorithm_name1": {
            comp_rate1: {
                "ped_avg": [list of ped_avg values],
                "sed_avg": [list of sed_avg values],
                "run_time": [list of run_time values]
            },
            comp_rate2: {
                ...
            },
            ...
    :rtype: dict[str, dict[float, dict[str, list]]]
    """
    alg_dict = {}
    for result in results:
        alg_name = result["algorithm_name"]
        if alg_name not in alg_dict:
            alg_dict[alg_name] = {}
        comp_rate = round(result["comp_ratio"], 2)
        if comp_rate not in alg_dict[alg_name]:
            alg_dict[alg_name][comp_rate] = {
                "ped_avg": [],
                "sed_avg": [],
                "run_time": [],
            }
        alg_dict[alg_name][comp_rate]["ped_avg"].append(result["ped_avg"])
        alg_dict[alg_name][comp_rate]["sed_avg"].append(result["sed_avg"])
        alg_dict[alg_name][comp_rate]["run_time"].append(result["run_time"])

    for alg_name in alg_dict:
        for comp_rate in alg_dict[alg_name]:
            for metric in alg_dict[alg_name][comp_rate]:
                values = alg_dict[alg_name][comp_rate][metric]
                avg_value = sum(values) / len(values)
                alg_dict[alg_name][comp_rate][metric] = avg_value
    return alg_dict


def process_results_jobs(results: list[dict]):
    alg_dict = compile_results_jobs(results)
    xs = []
    ys_peds = []
    ys_seds = []
    ys_runtimes = []
    alg_names = []

    for alg_name, data in alg_dict.items():
        if alg_name == "UNIFORM_SAMPLING":
            continue
        alg_names.append(alg_name)
        x, y_sed, y_ped, y_runtime = extract_lists(alg_dict, alg_name)
        xs.append(x)
        ys_peds.append(y_ped)
        ys_seds.append(y_sed)
        ys_runtimes.append(y_runtime)

    plot_metric_jobs(xs, ys_seds, "Avg. SED (m)", alg_names)
    plot_metric_jobs(xs, ys_peds, "Avg. PED (m)", alg_names)
    plot_metric_jobs(xs, ys_runtimes, "Runtime (points / s)", alg_names)


def plot_metric_jobs(
    x: list[list], y: list[list], metric: str, algorithm_names: list[str]
):
    plt.figure()
    plt.xlabel("Compression ratio")
    plt.ylabel(metric)
    for i, name in enumerate(algorithm_names):
        plt.plot(x[i], y[i], label=name)
    plt.legend()
    plt.show()
