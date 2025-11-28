import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


def sanitize_line(line: str):
    return line.replace('[0]: ', '').replace('\n', '').replace('(', '').replace(')', '')

base_dir = Path(__file__).resolve().parent  # .../P7/experiments
results_dir = os.path.join(base_dir, "math/logs_math")

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
            "run_time": 0.0
        }
        math = file.split('_')[-1].replace('.log', '')
        result["math"] = math
        with open(os.path.join(results_dir, file), 'r') as f:
            content = f.read()
            if content == "":
                continue
            parts = content.split(',')
            for part in parts:
                key, value = part.split(':')
                value = value.replace('\n', '')
                if 'algorithm_name' == key:
                    result['algorithm_name'] = value
                elif 'math' == key:
                    result['math'] = value
                elif 'ped_avg' == key:
                    result['ped_avg'] = float(value)
                elif 'ped_max' == key:
                    result['ped_max'] = float(value)
                elif 'sed_avg' == key:
                    result['sed_avg'] = float(value)
                elif 'sed_max' == key:
                    result['sed_max'] = float(value)
                elif 'comp_ratio' == key:
                    result['comp_ratio'] = float(value)
                elif 'run_time' == key:
                    result['run_time'] = float(value)
        results.append(result)

print(results)

circle = [r for r in results if r['math'] == 'circle']
ellipsoid = [r for r in results if r['math'] == 'ellipsoid']

def extract(data, key):
    return [d[key] for d in data]

# Prepare plots
fig1 = plt.figure()
plt.scatter(extract(circle,"comp_ratio"), extract(circle,"run_time"), label="circle")
plt.scatter(extract(ellipsoid,"comp_ratio"), extract(ellipsoid,"run_time"), label="ellipsoid")
plt.xlabel("comp_ratio")
plt.ylabel("run_time")
plt.legend()
plt.title("comp_ratio vs run_time")

fig2 = plt.figure()
plt.scatter(extract(circle,"comp_ratio"), extract(circle,"ped_avg"), label="circle")
plt.scatter(extract(ellipsoid,"comp_ratio"), extract(ellipsoid,"ped_avg"), label="ellipsoid")
plt.xlabel("comp_ratio")
plt.ylabel("ped_avg")
plt.legend()
plt.title("comp_ratio vs ped_avg")

fig3 = plt.figure()
plt.scatter(extract(circle,"comp_ratio"), extract(circle,"sed_avg"), label="circle")
plt.scatter(extract(ellipsoid,"comp_ratio"), extract(ellipsoid,"sed_avg"), label="ellipsoid")
plt.xlabel("comp_ratio")
plt.ylabel("sed_avg")
plt.legend()
plt.title("comp_ratio vs sed_avg")

#fig1.show()
#fig2.show()
#fig3.show()


def regression_line(x, y):
    x = np.array(x)
    y = np.array(y)

    coef = np.polyfit(x, y, 1)
    poly = np.poly1d(coef)

    xs = np.linspace(min(x), max(x), 200)
    ys = poly(xs)
    return xs, ys


# ----------------------
# REGRESSION PLOTS (LINES ONLY)
# ----------------------

# Regression for run_time
fig4 = plt.figure()
xs, ys = regression_line(extract(circle,"comp_ratio"), extract(circle,"run_time"))
plt.plot(xs, ys, label="circle")

xs, ys = regression_line(extract(ellipsoid,"comp_ratio"), extract(ellipsoid,"run_time"))
plt.plot(xs, ys, label="ellipsoid")

plt.xlabel("comp_ratio")
plt.ylabel("run_time (fit)")
plt.legend()
plt.title("Regression: comp_ratio vs run_time")

# Regression for ped_avg
fig5 = plt.figure()
xs, ys = regression_line(extract(circle,"comp_ratio"), extract(circle,"ped_avg"))
plt.plot(xs, ys, label="circle")

xs, ys = regression_line(extract(ellipsoid,"comp_ratio"), extract(ellipsoid,"ped_avg"))
plt.plot(xs, ys, label="ellipsoid")

plt.xlabel("comp_ratio")
plt.ylabel("ped_avg (fit)")
plt.legend()
plt.title("Regression: comp_ratio vs ped_avg")

# Regression for sed_avg
fig6 = plt.figure()
xs, ys = regression_line(extract(circle,"comp_ratio"), extract(circle,"sed_avg"))
plt.plot(xs, ys, label="circle")

xs, ys = regression_line(extract(ellipsoid,"comp_ratio"), extract(ellipsoid,"sed_avg"))
plt.plot(xs, ys, label="ellipsoid")

plt.xlabel("comp_ratio")
plt.ylabel("sed_avg (fit)")
plt.legend()
plt.title("Regression: comp_ratio vs sed_avg")

plt.show()