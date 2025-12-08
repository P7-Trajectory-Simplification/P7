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


def compile_results_math(
    results: list[dict],
) -> dict[str, dict[float, dict[str, list]]]:
    """
    Docstring for compile_results_math

    :param results: A list of result dictionaries containing the metrics "math", "algorithm_name", "ped_avg", "ped_max", "sed_avg", "sed_max", "run_time", and "comp_ratio"
    :type results: list[dict]
    :return: A dictionary mapping math types to compression rates to metrics, where each metric maps to a list of its recorded values.
    Structure is therefore
        {
        "circle": {
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
    math_dict = {}
    math_dict["circle"] = {}
    math_dict["ellipsoid"] = {}

    for result in results:
        comp_rate = round(result["comp_ratio"], 2)
        if comp_rate not in math_dict[result["math"]]:
            math_dict[result["math"]][comp_rate] = {
                "ped_avg": [],
                "sed_avg": [],
                "run_time": [],
            }
        math_dict[result["math"]][comp_rate]["ped_avg"].append(result["ped_avg"])
        math_dict[result["math"]][comp_rate]["sed_avg"].append(result["sed_avg"])
        math_dict[result["math"]][comp_rate]["run_time"].append(result["run_time"])

    for math_type in math_dict:
        for comp_rate in math_dict[math_type]:
            for metric in math_dict[math_type][comp_rate]:
                values = math_dict[math_type][comp_rate][metric]
                avg_value = sum(values) / len(values)
                math_dict[math_type][comp_rate][metric] = avg_value
    return math_dict


def process_results_math(results: list[dict]):
    math_dict = compile_results_math(results)

    x_circle, y_circle_sed, y_circle_ped, y_circle_runtime = extract_lists(
        math_dict, "circle"
    )
    x_ellipsoid, y_ellipsoid_sed, y_ellipsoid_ped, y_ellipsoid_runtime = extract_lists(
        math_dict, "ellipsoid"
    )

    plot_metric_math(
        x_circle, x_ellipsoid, y_circle_ped, y_ellipsoid_ped, "Avg. PED (m)"
    )
    plot_metric_math(
        x_circle, x_ellipsoid, y_circle_sed, y_ellipsoid_sed, "Avg. SED (m)"
    )
    plot_metric_math(
        x_circle,
        x_ellipsoid,
        y_circle_runtime,
        y_ellipsoid_runtime,
        "Runtime (points / s)",
    )


def plot_metric_math(x1: list, x2: list, y1: list, y2: list, metric: str):
    plt.figure()
    plt.xlabel("Compression ratio")
    plt.ylabel(metric)
    plt.plot(x1, y1, label="Sphere")
    plt.plot(x2, y2, label="Ellipsoid")
    plt.legend()
    plt.show()
