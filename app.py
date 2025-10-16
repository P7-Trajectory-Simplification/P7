from flask import Flask, request
from flask import render_template
from sqlalchemy import case
from algorithms.isolate_routes import isolate_routes
from data.database import get_all_vessels, get_vessel_logs
from algorithms.dp import douglas_peucker
from error_metrics.sed import sed_results
from error_metrics.ped import ped_results

app = Flask(__name__)



def get_data(csv_algorithms: str, end_time: str):
    
    vessel_one = get_all_vessels()[125]
    vessel_logs = get_vessel_logs(vessel_one.imo, "2024-01-01", end_time)
    routes = isolate_routes(vessel_logs)

    algorithms = csv_algorithms.split(',')
    response = {}
    for alg in algorithms:
        match alg:
            #case 'Ours':
            case 'DP':
                simplified_routes = []
                for route in routes:
                    simplified_routes.append(douglas_peucker(route, 0.001))

                response[alg] = routes_to_array(simplified_routes)
            #case 'SQUISH':
            #case 'SQUISH-E':
            
    response['raw'] = routes_to_array(routes)
    return response




def routes_to_array(routes):
    routes_array = []
    for route in routes:
        temp_array = []
        for log in route:
            temp_array.append((log.lat, log.lon, log.ts))
        routes_array.append(temp_array)
    return routes_array

def get_error_metrics(raw_routes, simplified_routes):
    error_metrics = []
    ped_avg, ped_max = ped_results(raw_routes, simplified_routes)
    sed_avg, sed_max = sed_results(raw_routes, simplified_routes)
    error_metrics = [ped_avg, ped_max, sed_avg, sed_max]
    return error_metrics

@app.route('/')
def index():
    return render_template('index.html.jinja', algorithms=['Ours', 'SQUISH', 'SQUISH-E', 'DP'])

@app.route('/algorithm')
def get_algorithm_ours():
    algs = request.args.get("algs")
    end_time = request.args.get("end_time")
    print(end_time)
    return get_data(algs, end_time)

@app.route('/error-metrics', methods=['POST'])
def get_error_metrics_request():
    algs = request.args.get("algs")
    raw_data = request.json['raw_data']
    simplified_data = request.json['simplified_data']
    all_error_metrics = [[]]
    for alg in algs.split(','):
        match alg:
            case 'DP':
                all_error_metrics.append(get_error_metrics(raw_data, simplified_data))
    return get_error_metrics(raw_data, simplified_data)


"""case 'Ours':
                all_error_metrics.append(get_error_metrics(raw_data, simplified_data))
            case 'SQUISH':
                all_error_metrics.append(get_error_metrics(raw_data, simplified_data))
            case 'SQUISH-E':
                all_error_metrics.append(get_error_metrics(raw_data, simplified_data))"""