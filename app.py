from flask import Flask, request
from flask import render_template
from sqlalchemy import case
from algorithms.isolate_routes import isolate_routes
from data.database import get_all_vessels, get_vessel_logs
from algorithms.dp import douglas_peucker
from algorithms.squish import squish
from vessel_log import VesselLog

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
                    simplified_routes.append(douglas_peucker(route["route"], 0.001))

                response[alg] = routes_to_array(simplified_routes)
            case 'SQUISH':
                simplified_routes = []
                for route in routes:
                    squish(route["route"], route["squish_buff"])
                    temp = []
                    for item in route["squish_buff"]:
                        temp.append(item[0])
                    simplified_routes.append(temp)
                response[alg] = routes_to_array(simplified_routes)

            #case 'SQUISH-E':
    temp = []
    for route in routes:
        temp.append(route['route'])

    response['raw'] = routes_to_array(temp)
    return response




def routes_to_array(routes: list[list[VesselLog]]):
    routes_array = []
    for route in routes:
        temp_array = []
        for log in route:
            temp_array.append((log.lat, log.lon, log.ts))
        routes_array.append(temp_array)
    return routes_array


@app.route('/')
def index():
    return render_template('index.html.jinja', algorithms=['Ours', 'SQUISH', 'SQUISH-E', 'DP'])

@app.route('/algorithm')
def get_algorithm_ours():
    algs = request.args.get("algs")
    end_time = request.args.get("end_time")
    print(end_time)
    return get_data(algs, end_time)